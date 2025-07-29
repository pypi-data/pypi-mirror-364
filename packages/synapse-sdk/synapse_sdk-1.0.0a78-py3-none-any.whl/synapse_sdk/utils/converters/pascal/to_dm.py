import os
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

from synapse_sdk.utils.converters import ToDMConverter


class PascalToDMConverter(ToDMConverter):
    """Convert Pascal VOC formatted datasets to DM format."""

    IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp']

    def convert(self):
        """Convert the Pascal VOC dataset to DM format."""
        if self.is_categorized_dataset:
            splits = self._validate_splits(['train', 'valid'], ['test'])
            all_split_data = {}
            for split, split_dir in splits.items():
                split_data = self._convert_pascal_split_to_dm(split_dir)
                all_split_data[split] = split_data
            self.converted_data = all_split_data
            return all_split_data
        else:
            split_data = self._convert_pascal_split_to_dm(self.root_dir)
            self.converted_data = split_data
            return split_data

    def _find_image_path(self, images_dir: str, filename: str) -> Optional[str]:
        """Find the image file in the specified directory."""
        img_path = os.path.join(images_dir, filename)
        if os.path.exists(img_path):
            return img_path
        base = os.path.splitext(filename)[0]
        for ext in self.IMG_EXTENSIONS:
            img_path = os.path.join(images_dir, base + ext)
            if os.path.exists(img_path):
                return img_path
        return None

    @staticmethod
    def _get_image_size(image_path: str) -> Tuple[int, int]:
        """Get the size of the image."""
        with Image.open(image_path) as img:
            return img.size

    def _parse_pascal_xml(self, xml_path: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Parse a Pascal VOC XML file and return the filename and objects."""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        filename_elem = root.find('filename')
        filename = filename_elem.text if filename_elem is not None else None
        objects = []
        for obj in root.findall('object'):
            name_elem = obj.find('name')
            bndbox_elem = obj.find('bndbox')
            if name_elem is None or bndbox_elem is None:
                continue
            class_name = name_elem.text
            xmin_elem = bndbox_elem.find('xmin')
            ymin_elem = bndbox_elem.find('ymin')
            xmax_elem = bndbox_elem.find('xmax')
            ymax_elem = bndbox_elem.find('ymax')
            if any(elem is None for elem in [xmin_elem, ymin_elem, xmax_elem, ymax_elem]):
                continue
            xmin = int(float(xmin_elem.text))
            ymin = int(float(ymin_elem.text))
            xmax = int(float(xmax_elem.text))
            ymax = int(float(ymax_elem.text))
            width = xmax - xmin
            height = ymax - ymin
            objects.append({'classification': class_name, 'data': [xmin, ymin, width, height]})
        return filename, objects

    def _convert_pascal_split_to_dm(self, split_dir: str) -> Dict[str, Any]:
        """Convert a single Pascal VOC split directory to DM format."""
        annotations_dir = None
        for candidate in ['Annotations', 'annotations']:
            candidate_path = os.path.join(split_dir, candidate)
            if os.path.isdir(candidate_path):
                annotations_dir = candidate_path
                break
        if annotations_dir is None:
            raise FileNotFoundError(
                f"No annotations directory found in {split_dir} (tried 'Annotations', 'annotations')."
            )
        images_dir = None
        for candidate in ['Images', 'images', 'JPEGImages']:
            candidate_path = os.path.join(split_dir, candidate)
            if os.path.isdir(candidate_path):
                images_dir = candidate_path
                break
        if images_dir is None:
            raise FileNotFoundError(
                f"No images directory found in {split_dir} (tried 'Images', 'images', 'JPEGImages')."
            )
        result = {}
        for xml_filename in os.listdir(annotations_dir):
            if not xml_filename.endswith('.xml'):
                continue
            xml_path = os.path.join(annotations_dir, xml_filename)
            try:
                filename, objects = self._parse_pascal_xml(xml_path)
                if filename is None:
                    print(f'[WARNING] No filename found in {xml_filename}, skipping.')
                    continue
                img_path = self._find_image_path(images_dir, filename)
                if img_path is None:
                    print(f'[WARNING] Image not found for {filename}, skipping.')
                    continue
                # Prepare DM annotation structure
                dm_img = {
                    'bounding_box': [],
                    'polygon': [],
                    'keypoint': [],
                    'relation': [],
                    'group': [],
                }
                for obj in objects:
                    dm_img['bounding_box'].append({
                        'id': self._generate_unique_id(),
                        'classification': obj['classification'],
                        'attrs': [],
                        'data': obj['data'],
                    })
                dm_json = {'images': [dm_img]}
                result[os.path.basename(img_path)] = (dm_json, img_path)
            except ET.ParseError as e:
                print(f'[WARNING] Failed to parse {xml_filename}: {e}, skipping.')
                continue
            except Exception as e:
                print(f'[WARNING] Error processing {xml_filename}: {e}, skipping.')
                continue
        return result
