import random
import string

from . import BaseDMConverter


class DMV2ToV1Converter(BaseDMConverter):
    """DM v2 to v1 format converter class."""

    def __init__(self, new_dm_data={}):
        """Initialize the converter.

        Args:
            new_dm_data (dict): DM v2 format data to be converted
        """
        super().__init__()
        self.new_dm_data = new_dm_data
        self.annotations = {}
        self.annotations_data = {}
        self.extra = {}
        self.relations = {}
        self.annotation_groups = {}

    def convert(self):
        """Convert DM v2 data to v1 format.

        Returns:
            dict: Converted data in DM v1 format
        """
        # Reset state
        new_dm_data = self.new_dm_data
        self.annotations = {}
        self.annotations_data = {}
        self.extra = {}
        self.relations = {}
        self.annotation_groups = {}

        # Process each media type (images, videos, etc.)
        for media_type_plural, media_items in new_dm_data.items():
            if media_type_plural == 'classification':
                continue

            media_type = self._singularize_media_type(media_type_plural)

            for index, media_item in enumerate(media_items, 1):
                media_id = f'{media_type}_{index}'

                # Initialize structures for this media
                self.annotations[media_id] = []
                self.annotations_data[media_id] = []
                self.extra[media_id] = {}
                self.relations[media_id] = []
                self.annotation_groups[media_id] = []

                # Process each tool type in the media item
                for tool_type, tool_data in media_item.items():
                    self._process_tool_data(media_id, tool_type, tool_data)

        # Build final result
        result = {
            'extra': self.extra,
            'relations': self.relations,
            'annotations': self.annotations,
            'annotationsData': self.annotations_data,
            'annotationGroups': self.annotation_groups,
        }

        return result

    def _process_tool_data(self, media_id, tool_type, tool_data):
        """Process tool data for a specific media item.

        Args:
            media_id (str): ID of the media item
            tool_type (str): Type of annotation tool
            tool_data (list): List of annotation data for this tool
        """
        for annotation in tool_data:
            annotation_id = annotation['id']
            classification = annotation['classification']
            attrs = annotation.get('attrs', [])
            data = annotation.get('data', {})

            # Create annotation entry
            annotation_entry = {
                'id': annotation_id,
                'tool': tool_type,
                'isLocked': False,
                'isVisible': True,
                'classification': {'class': classification},
            }

            # Add additional classification attributes from attrs
            for attr in attrs:
                attr_name = attr.get('name')
                attr_value = attr.get('value')
                if attr_name and attr_value is not None:
                    annotation_entry['classification'][attr_name] = attr_value

            # Add special attributes for specific tools
            if tool_type == 'keypoint':
                annotation_entry['shape'] = 'circle'

            self.annotations[media_id].append(annotation_entry)

            # Create annotations data entry using tool processor
            processor = self.tool_processors.get(tool_type)
            if processor:
                processor(annotation_id, data, self.annotations_data[media_id])
            else:
                self._handle_unknown_tool(tool_type, annotation_id)

    def _process_bounding_box(self, annotation_id, data, annotations_data):
        """Process bounding box annotation data.

        Args:
            annotation_id (str): ID of the annotation
            data (list): Bounding box data [x1, y1, x2, y2]
            annotations_data (list): List to append the processed data
        """
        if len(data) >= 4:
            x1, y1, width, height = data[:4]
            coordinate = {'x': x1, 'y': y1, 'width': width, 'height': height}

            annotations_data.append({'id': annotation_id, 'coordinate': coordinate})

    def _process_named_entity(self, annotation_id, data, annotations_data):
        """Process named entity annotation data.

        Args:
            annotation_id (str): ID of the annotation
            data (dict): Named entity data with ranges and content
            annotations_data (list): List to append the processed data
        """
        entity_data = {'id': annotation_id}

        if 'ranges' in data:
            entity_data['ranges'] = data['ranges']

        if 'content' in data:
            entity_data['content'] = data['content']

        annotations_data.append(entity_data)

    def _process_classification(self, annotation_id, data, annotations_data):
        """Process classification annotation data.

        Args:
            annotation_id (str): ID of the annotation
            data (dict): Classification data (usually empty)
            annotations_data (list): List to append the processed data
        """
        # Classification data is typically empty in v2, so we just add the ID
        annotations_data.append({'id': annotation_id})

    def _process_polyline(self, annotation_id, data, annotations_data):
        """Process polyline annotation data.

        Args:
            annotation_id (str): ID of the annotation
            data (list): Polyline data [x1, y1, x2, y2, ...]
            annotations_data (list): List to append the processed data
        """
        # Convert flat array to coordinate objects
        coordinates = []
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                coordinates.append({'x': data[i], 'y': data[i + 1], 'id': self._generate_random_id()})

        annotations_data.append({'id': annotation_id, 'coordinate': coordinates})

    def _process_keypoint(self, annotation_id, data, annotations_data):
        """Process keypoint annotation data.

        Args:
            annotation_id (str): ID of the annotation
            data (list): Keypoint data [x, y]
            annotations_data (list): List to append the processed data
        """
        if len(data) >= 2:
            coordinate = {'x': data[0], 'y': data[1]}

            annotations_data.append({'id': annotation_id, 'coordinate': coordinate})

    def _process_3d_bounding_box(self, annotation_id, data, annotations_data):
        """Process 3D bounding box annotation data.

        Args:
            annotation_id (str): ID of the annotation
            data (dict): 3D bounding box PSR data
            annotations_data (list): List to append the processed data
        """
        annotations_data.append({'id': annotation_id, 'psr': data})

    def _process_segmentation(self, annotation_id, data, annotations_data):
        """Process segmentation annotation data.

        Args:
            annotation_id (str): ID of the annotation
            data (list or dict): Segmentation data (pixel_indices or section)
            annotations_data (list): List to append the processed data
        """
        annotation_data = {'id': annotation_id}

        if isinstance(data, list):
            # Pixel-based segmentation
            annotation_data['pixel_indices'] = data
        elif isinstance(data, dict):
            # Section-based segmentation (video)
            annotation_data['section'] = data

        annotations_data.append(annotation_data)

    def _process_polygon(self, annotation_id, data, annotations_data):
        """Process polygon annotation data.

        Args:
            annotation_id (str): ID of the annotation
            data (list): Polygon data [x1, y1, x2, y2, ...]
            annotations_data (list): List to append the processed data
        """
        # Convert flat array to coordinate objects
        coordinates = []
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                coordinates.append({'x': data[i], 'y': data[i + 1], 'id': self._generate_random_id()})

        annotations_data.append({'id': annotation_id, 'coordinate': coordinates})

    def _process_relation(self, annotation_id, data, annotations_data):
        """Process relation annotation data.

        Args:
            annotation_id (str): ID of the annotation
            data (list): Relation data
            annotations_data (list): List to append the processed data
        """
        annotations_data.append({'id': annotation_id, 'data': data})

    def _process_group(self, annotation_id, data, annotations_data):
        """Process group annotation data.

        Args:
            annotation_id (str): ID of the annotation
            data (list): Group data
            annotations_data (list): List to append the processed data
        """
        annotations_data.append({'id': annotation_id, 'data': data})

    def _generate_random_id(self):
        """Generate a random ID similar to the original format."""
        # Generate 10-character random string with letters, numbers, and symbols
        chars = string.ascii_letters + string.digits + '-_'
        return ''.join(random.choices(chars, k=10))
