from abc import ABC, abstractmethod


class BaseDMConverter(ABC):
    """Base class for DM format converters."""

    SUPPORTED_TOOLS = [
        'bounding_box',
        'named_entity',
        'classification',
        'polyline',
        'keypoint',
        '3d_bounding_box',
        'segmentation',
        'polygon',
        'relation',
        'group',
    ]

    def __init__(self):
        """Initialize the base converter."""
        self.tool_processors = self._setup_tool_processors()

    def _setup_tool_processors(self):
        """Setup tool processor mapping."""
        return {
            'bounding_box': self._process_bounding_box,
            'named_entity': self._process_named_entity,
            'classification': self._process_classification,
            'polyline': self._process_polyline,
            'keypoint': self._process_keypoint,
            '3d_bounding_box': self._process_3d_bounding_box,
            'segmentation': self._process_segmentation,
            'polygon': self._process_polygon,
            'relation': self._process_relation,
            'group': self._process_group,
        }

    @abstractmethod
    def convert(self):
        """Convert data from one format to another."""
        pass

    @abstractmethod
    def _process_bounding_box(self, *args, **kwargs):
        """Process bounding box annotation."""
        pass

    @abstractmethod
    def _process_named_entity(self, *args, **kwargs):
        """Process named entity annotation."""
        pass

    @abstractmethod
    def _process_classification(self, *args, **kwargs):
        """Process classification annotation."""
        pass

    @abstractmethod
    def _process_polyline(self, *args, **kwargs):
        """Process polyline annotation."""
        pass

    @abstractmethod
    def _process_keypoint(self, *args, **kwargs):
        """Process keypoint annotation."""
        pass

    @abstractmethod
    def _process_3d_bounding_box(self, *args, **kwargs):
        """Process 3D bounding box annotation."""
        pass

    @abstractmethod
    def _process_segmentation(self, *args, **kwargs):
        """Process segmentation annotation."""
        pass

    @abstractmethod
    def _process_polygon(self, *args, **kwargs):
        """Process polygon annotation."""
        pass

    @abstractmethod
    def _process_relation(self, *args, **kwargs):
        """Process relation annotation."""
        pass

    @abstractmethod
    def _process_group(self, *args, **kwargs):
        """Process group annotation."""
        pass

    def _handle_unknown_tool(self, tool_type, item_id=None):
        """Handle unknown tool types with consistent warning message."""
        warning_msg = f"Warning: Unknown tool type '{tool_type}'"
        if item_id:
            warning_msg += f' for item {item_id}'
        print(warning_msg)

    def _extract_media_type_info(self, media_id):
        """Extract media type information from media ID."""
        media_type = media_id.split('_')[0] if '_' in media_id else media_id
        media_type_plural = media_type + 's' if not media_type.endswith('s') else media_type
        return media_type, media_type_plural

    def _singularize_media_type(self, media_type_plural):
        """Convert plural media type to singular."""
        return media_type_plural.rstrip('s')
