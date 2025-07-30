from . import BaseDMConverter


class DMV1ToV2Converter(BaseDMConverter):
    """DM v1 to v2 format converter class."""

    def __init__(self, old_dm_data={}):
        """Initialize the converter.

        Args:
            old_dm_data (dict): DM v1 format data to be converted
        """
        super().__init__()
        self.old_dm_data = old_dm_data
        self.classification_info = {}
        self.media_data = {}

    def convert(self):
        """Convert DM v1 data to v2 format.

        Returns:
            dict: Converted data in DM v2 format
        """
        # Reset state
        old_dm_data = self.old_dm_data
        self.classification_info = {}
        self.media_data = {}

        # Extract media IDs from annotations key
        media_ids = list(old_dm_data.get('annotations', {}).keys())

        for media_id in media_ids:
            self._process_media_item(old_dm_data, media_id)

        # Build final result (put classification at the front)
        result = {'classification': self.classification_info}
        result.update(self.media_data)

        return result

    def _process_media_item(self, old_dm_data, media_id):
        """Process a single media item.

        Args:
            old_dm_data (dict): Original DM v1 data
            media_id (str): ID of the media item to process
        """
        # Extract media type (e.g., "video_1" -> "videos", "image_2" -> "images")
        media_type, media_type_plural = self._extract_media_type_info(media_id)

        # Create list for this media type if it doesn't exist
        if media_type_plural not in self.media_data:
            self.media_data[media_type_plural] = []

        # Create id -> class and tool mappings
        id_to_class = {
            annotation['id']: annotation['classification']['class']
            for annotation in old_dm_data['annotations'][media_id]
        }

        id_to_tool = {annotation['id']: annotation['tool'] for annotation in old_dm_data['annotations'][media_id]}

        # Create id -> full classification mapping (including additional attributes)
        id_to_full_classification = {
            annotation['id']: annotation['classification'] for annotation in old_dm_data['annotations'][media_id]
        }

        # Initialize current media item
        media_item = {}

        # Process data from annotationsData for this media
        annotations_data = old_dm_data.get('annotationsData', {}).get(media_id, [])

        # Group by annotation tool type
        tools_data = {}

        for item in annotations_data:
            item_id = item.get('id', '')
            # Get tool and classification info from annotations
            tool_type = id_to_tool.get(item_id, '')
            classification = id_to_class.get(item_id, '')

            # Collect classification info (maintain existing ID)
            if tool_type not in self.classification_info:
                self.classification_info[tool_type] = []

            # Add only non-duplicate classifications
            if classification and classification not in self.classification_info[tool_type]:
                self.classification_info[tool_type].append(classification)

            # Process by each tool type
            self._process_annotation_item(
                item, item_id, tool_type, classification, id_to_full_classification, tools_data
            )

        # Add processed tool data to media item
        for tool_type, tool_data in tools_data.items():
            if tool_data:  # Only add if data exists
                media_item[tool_type] = tool_data

        # Add media item to result (only if data exists)
        if media_item:
            self.media_data[media_type_plural].append(media_item)

    def _process_annotation_item(self, item, item_id, tool_type, classification, id_to_full_classification, tools_data):
        """Process a single annotation item based on its tool type.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            tool_type (str): Type of annotation tool
            classification (str): Classification label
            id_to_full_classification (dict): Mapping of ID to full classification data
            tools_data (dict): Dictionary to store processed tool data
        """
        processor = self.tool_processors.get(tool_type)
        if processor:
            processor(item, item_id, classification, tools_data, id_to_full_classification)
        else:
            # Handle unknown tool_type
            self._handle_unknown_tool(tool_type, item_id)

    def _process_bounding_box(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process bounding box annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'bounding_box' not in tools_data:
            tools_data['bounding_box'] = []

        # Process coordinate or coordinates
        coord_data = None
        if 'coordinate' in item and isinstance(item['coordinate'], dict):
            # Single coordinate structure (dictionary)
            coord_data = item['coordinate']
        elif 'coordinates' in item:
            # Multiple coordinates structure (video etc.)
            coords_data = item['coordinates']
            if coords_data:
                # Use coordinate data from first key
                first_key = list(coords_data.keys())[0]
                coord_data = coords_data[first_key]

        if coord_data and 'width' in coord_data and 'height' in coord_data:
            data = [
                coord_data['x'],
                coord_data['y'],
                coord_data['width'],
                coord_data['height'],
            ]

            tools_data['bounding_box'].append({
                'id': item_id,
                'classification': classification,
                'attrs': [],
                'data': data,
            })

    def _process_named_entity(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process named entity annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'named_entity' not in tools_data:
            tools_data['named_entity'] = []

        # Process named_entity ranges and content
        entity_data = {}
        if 'ranges' in item and isinstance(item['ranges'], list):
            # Store ranges information
            entity_data['ranges'] = item['ranges']

        if 'content' in item:
            # Store selected text content
            entity_data['content'] = item['content']

        tools_data['named_entity'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': entity_data,  # Format: {ranges: [...], content: "..."}
        })

    def _process_classification(self, item, item_id, classification, tools_data, id_to_full_classification):
        """Process classification annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict): Full classification mapping
        """
        if 'classification' not in tools_data:
            tools_data['classification'] = []

        # Get full classification info (including additional attributes)
        full_classification = id_to_full_classification.get(item_id, {})

        # Store additional attributes in attrs array
        attrs = []
        classification_data = {}

        for key, value in full_classification.items():
            if key != 'class':  # class is already stored in classification field
                if isinstance(value, list) and len(value) > 0:
                    # Array attributes like multiple
                    attrs.append({'name': key, 'value': value})
                elif isinstance(value, str) and value.strip():
                    # String attributes like text, single_radio, single_dropdown
                    attrs.append({'name': key, 'value': value})

        tools_data['classification'].append({
            'id': item_id,
            'classification': classification,
            'attrs': attrs,
            'data': classification_data,  # Empty object for full text classification
        })

    def _process_polyline(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process polyline annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'polyline' not in tools_data:
            tools_data['polyline'] = []

        # Process polyline coordinates
        polyline_data = []
        if 'coordinate' in item and isinstance(item['coordinate'], list):
            # Convert each coordinate point to [x, y] format
            for point in item['coordinate']:
                if 'x' in point and 'y' in point:
                    polyline_data.extend([point['x'], point['y']])

        tools_data['polyline'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': polyline_data,  # Format: [x1, y1, x2, y2, x3, y3, ...]
        })

    def _process_keypoint(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process keypoint annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'keypoint' not in tools_data:
            tools_data['keypoint'] = []

        # Process keypoint coordinate (single point)
        keypoint_data = []
        if 'coordinate' in item and isinstance(item['coordinate'], dict):
            coord = item['coordinate']
            if 'x' in coord and 'y' in coord:
                keypoint_data = [coord['x'], coord['y']]

        tools_data['keypoint'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': keypoint_data,  # Format: [x, y]
        })

    def _process_3d_bounding_box(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process 3D bounding box annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if '3d_bounding_box' not in tools_data:
            tools_data['3d_bounding_box'] = []

        # Process 3d_bounding_box psr (position, scale, rotation)
        psr_data = {}
        if 'psr' in item and isinstance(item['psr'], dict):
            psr_data = item['psr']

        tools_data['3d_bounding_box'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': psr_data,  # Format: {position: {x,y,z}, scale: {x,y,z}, rotation: {x,y,z}}
        })

    def _process_segmentation(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process segmentation annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'segmentation' not in tools_data:
            tools_data['segmentation'] = []

        # Process segmentation pixel_indices or section
        segmentation_data = {}
        if 'pixel_indices' in item and isinstance(item['pixel_indices'], list):
            # Pixel-based segmentation (images)
            segmentation_data = item['pixel_indices']
        elif 'section' in item and isinstance(item['section'], dict):
            # Frame section-based segmentation (videos)
            segmentation_data = item['section']

        tools_data['segmentation'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': segmentation_data,  # Format: [pixel_indices...] or {startFrame: x, endFrame: y}
        })

    def _process_polygon(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process polygon annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'polygon' not in tools_data:
            tools_data['polygon'] = []

        # Process polygon coordinates
        polygon_data = []
        if 'coordinate' in item and isinstance(item['coordinate'], list):
            # Convert each coordinate point to [x, y] format
            for point in item['coordinate']:
                if 'x' in point and 'y' in point:
                    polygon_data.extend([point['x'], point['y']])

        tools_data['polygon'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': polygon_data,  # Format: [x1, y1, x2, y2, x3, y3, ...]
        })

    def _process_relation(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process relation annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'relation' not in tools_data:
            tools_data['relation'] = []

        # Process relation data (needs adjustment based on actual relation data structure)
        relation_data = []
        if 'data' in item:
            relation_data = item['data']

        tools_data['relation'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': relation_data,  # Format: ['from_id', 'to_id']
        })

    def _process_group(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process group annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'group' not in tools_data:
            tools_data['group'] = []

        # Process group data (needs adjustment based on actual group data structure)
        group_data = []
        if 'data' in item:
            group_data = item['data']

        tools_data['group'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': group_data,  # Format: ['id1', 'id2', 'id3', ...]
        })
