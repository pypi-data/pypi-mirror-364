import os
from typing import Any, Dict, List, Tuple

import yaml
from PIL import Image

from synapse_sdk.utils.converters import ToDMConverter


class YOLOToDMConverter(ToDMConverter):
    """Convert YOLO formatted datasets to DM format."""

    IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp']

    def convert(self):
        """Convert YOLO dataset to DM format."""
        if self.is_categorized_dataset:
            splits = self._validate_splits(['train', 'valid'], ['test'])
            all_split_data = {}
            for split, split_dir in splits.items():
                split_data = self._convert_yolo_split_to_dm(split_dir)
                all_split_data[split] = split_data
            self.converted_data = all_split_data
            return all_split_data
        else:
            split_data = self._convert_yolo_split_to_dm(self.root_dir)
            self.converted_data = split_data
            return split_data

    def _find_image_path(self, images_dir, base):
        """Find the image file corresponding to the base name in the images directory."""
        for ext in self.IMG_EXTENSIONS:
            img_path = os.path.join(images_dir, base + ext)
            if os.path.exists(img_path):
                return img_path
        return None

    @staticmethod
    def _get_image_size(image_path: str) -> Tuple[int, int]:
        """Get the size of the image at the given path."""
        with Image.open(image_path) as img:
            return img.size

    def _parse_yolo_line(self, line: str, class_names: List[str], img_size: Tuple[int, int]):
        """Parse a single line from a YOLO label file."""
        parts = line.strip().split()
        if len(parts) < 5:
            return None  # skip malformed

        class_idx = int(parts[0])
        class_name = class_names[class_idx] if class_idx < len(class_names) else f'class_{class_idx}'
        img_w, img_h = img_size

        # Check if it's a polygon (more than 5 values and even number of coordinates after class_id)
        if len(parts) > 5 and (len(parts) - 1) % 2 == 0:
            # Polygon format: class_id x1 y1 x2 y2 x3 y3 ... (normalized coordinates)
            coords = []
            for i in range(1, len(parts), 2):
                x_norm = float(parts[i])
                y_norm = float(parts[i + 1])
                # Convert normalized coordinates to absolute coordinates
                x_abs = int(x_norm * img_w)
                y_abs = int(y_norm * img_h)
                coords.append([x_abs, y_abs])

            return {'type': 'polygon', 'classification': class_name, 'data': coords}

        # Standard bounding box format
        elif len(parts) == 5:
            x_center, y_center, width, height = map(float, parts[1:5])

            # Denormalize YOLO (x_center, y_center, w, h) to (left, top, w, h)
            left = int((x_center - width / 2) * img_w)
            top = int((y_center - height / 2) * img_h)
            abs_w = int(width * img_w)
            abs_h = int(height * img_h)

            return {'type': 'bounding_box', 'classification': class_name, 'data': [left, top, abs_w, abs_h]}

        # Keypoint format: class_id x_center y_center w h x1 y1 v1 x2 y2 v2 ...
        elif len(parts) > 5 and (len(parts) - 5) % 3 == 0:
            x_center, y_center, width, height = map(float, parts[1:5])

            # Denormalize bounding box
            left = int((x_center - width / 2) * img_w)
            top = int((y_center - height / 2) * img_h)
            abs_w = int(width * img_w)
            abs_h = int(height * img_h)

            keypoints = []
            for i in range(5, len(parts), 3):
                xk = int(float(parts[i]) * img_w)
                yk = int(float(parts[i + 1]) * img_h)
                vk = int(parts[i + 2])
                keypoints.append([xk, yk, vk])

            return {
                'type': 'keypoint',
                'classification': class_name,
                'data': keypoints,
                'bounding_box': [left, top, abs_w, abs_h],
            }

        return None

    def _convert_yolo_split_to_dm(self, split_dir: str) -> Dict[str, Any]:
        """Convert a single YOLO split directory to DM format."""
        # Find image and label directories
        images_dir = None
        for candidate in ['images', 'img', 'imgs']:
            candidate_path = os.path.join(split_dir, candidate)
            if os.path.isdir(candidate_path):
                images_dir = candidate_path
                break
        if images_dir is None:
            raise FileNotFoundError(f"No images directory found in {split_dir} (tried 'images', 'img', 'imgs').")

        labels_dir = os.path.join(split_dir, 'labels')
        if not os.path.isdir(labels_dir):
            raise FileNotFoundError(f"No labels directory found in {split_dir} (expected 'labels').")

        # Load dataset.yaml

        dataset_yaml_path = os.path.join(self.root_dir, 'dataset.yaml')
        if not os.path.exists(dataset_yaml_path):
            raise FileNotFoundError(f'No dataset.yaml file found in {split_dir}.')
        with open(dataset_yaml_path, 'r', encoding='utf-8') as f:
            dataset_yaml = yaml.safe_load(f)
            class_names = dataset_yaml.get('names', [])

        # Build DM data
        result = {}
        for label_filename in os.listdir(labels_dir):
            if not label_filename.endswith('.txt'):
                continue
            base = os.path.splitext(label_filename)[0]
            img_path = self._find_image_path(images_dir, base)
            if img_path is None:
                print(f'[WARNING] Image not found for label {label_filename}, skipping.')
                continue
            img_size = self._get_image_size(img_path)
            label_path = os.path.join(labels_dir, label_filename)
            with open(label_path, 'r', encoding='utf-8') as f:
                label_lines = [line.strip() for line in f if line.strip()]

            # Prepare DM annotation structure
            dm_img = {
                'bounding_box': [],
                'polygon': [],
                'keypoint': [],
                'relation': [],
                'group': [],
            }

            for line in label_lines:
                ann = self._parse_yolo_line(line, class_names, img_size)
                if ann is None:
                    continue

                if ann['type'] == 'bounding_box':
                    dm_img['bounding_box'].append({
                        'id': self._generate_unique_id(),
                        'classification': ann['classification'],
                        'attrs': [],
                        'data': ann['data'],
                    })
                elif ann['type'] == 'polygon':
                    dm_img['polygon'].append({
                        'id': self._generate_unique_id(),
                        'classification': ann['classification'],
                        'attrs': [],
                        'data': ann['data'],
                    })
                elif ann['type'] == 'keypoint':
                    dm_img['keypoint'].append({
                        'id': self._generate_unique_id(),
                        'classification': ann['classification'],
                        'attrs': [],
                        'data': ann['data'],
                        'bounding_box': ann['bounding_box'],
                    })

            dm_json = {'images': [dm_img]}
            result[os.path.basename(img_path)] = (dm_json, img_path)
        return result
