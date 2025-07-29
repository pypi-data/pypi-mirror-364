import unittest
from pixel_canon.core import ImageLayout, ImageAxis, MemoryOrder, ChannelFormat, AxisDirection
from pixel_canon.common import CommonLayouts
from pixel_canon.utils import get_speed_order, are_layouts_memory_equivalent

class TestUtils(unittest.TestCase):

    def test_get_speed_order(self):
        """Test the calculation of axis speed order."""
        # Row major: reversed axis_order
        hwc_rm = CommonLayouts.HWC_ROW_MAJOR_RGB
        expected_hwc_rm = [ImageAxis.CHANNELS, ImageAxis.WIDTH, ImageAxis.HEIGHT]
        self.assertEqual(get_speed_order(hwc_rm), expected_hwc_rm)
        
        # Column major: same as axis_order
        cwh_cm = CommonLayouts.CWH_COLUMN_MAJOR_RGB
        expected_cwh_cm = [ImageAxis.CHANNELS, ImageAxis.WIDTH, ImageAxis.HEIGHT]
        self.assertEqual(get_speed_order(cwh_cm), expected_cwh_cm)
        
        chw_rm = CommonLayouts.CHW_ROW_MAJOR_RGB
        expected_chw_rm = [ImageAxis.WIDTH, ImageAxis.HEIGHT, ImageAxis.CHANNELS]
        self.assertEqual(get_speed_order(chw_rm), expected_chw_rm)

    def test_are_layouts_memory_equivalent_positive(self):
        """Test cases where layouts ARE memory-equivalent."""
        # A layout is equivalent to itself
        self.assertTrue(are_layouts_memory_equivalent(
            CommonLayouts.HWC_ROW_MAJOR_RGB,
            CommonLayouts.HWC_ROW_MAJOR_RGB
        ))
        
        # The canonical C vs Fortran case
        self.assertTrue(are_layouts_memory_equivalent(
            CommonLayouts.HWC_ROW_MAJOR_RGB,
            CommonLayouts.CWH_COLUMN_MAJOR_RGB
        ))
        
        # Test that directions and channel names are ignored
        layout1 = ImageLayout(
            axis_order=(ImageAxis.HEIGHT, ImageAxis.WIDTH, ImageAxis.CHANNELS),
            memory_order=MemoryOrder.ROW_MAJOR,
            channels=ChannelFormat.RGB,
            directions={ImageAxis.HEIGHT: AxisDirection.DOWN}
        )
        layout2 = ImageLayout(
            axis_order=(ImageAxis.HEIGHT, ImageAxis.WIDTH, ImageAxis.CHANNELS),
            memory_order=MemoryOrder.ROW_MAJOR,
            channels=ChannelFormat.BGR,  # Different channel order
            directions={ImageAxis.HEIGHT: AxisDirection.UP} # Different direction
        )
        self.assertTrue(are_layouts_memory_equivalent(layout1, layout2))

    def test_are_layouts_memory_equivalent_negative(self):
        """Test cases where layouts are NOT memory-equivalent."""
        # Different axis order with same memory order
        self.assertFalse(are_layouts_memory_equivalent(
            CommonLayouts.HWC_ROW_MAJOR_RGB,
            CommonLayouts.CHW_ROW_MAJOR_RGB
        ))
        
        # Different number of axes
        hw_layout = ImageLayout(
            axis_order=(ImageAxis.HEIGHT, ImageAxis.WIDTH),
            memory_order=MemoryOrder.ROW_MAJOR,
            channels=ChannelFormat.LUMINANCE,
            directions={}
        )
        self.assertFalse(are_layouts_memory_equivalent(
            CommonLayouts.HWC_ROW_MAJOR_RGB,
            hw_layout
        ))
        
        # Same axes, different set (e.g. D vs C)
        dhw_layout = ImageLayout(
            axis_order=(ImageAxis.DEPTH, ImageAxis.HEIGHT, ImageAxis.WIDTH),
            memory_order=MemoryOrder.ROW_MAJOR,
            channels="",
            directions={}
        )
        self.assertFalse(are_layouts_memory_equivalent(
            CommonLayouts.CHW_ROW_MAJOR_RGB,
            dhw_layout
        ))
        
        # Same axis_order, different memory_order
        hwc_cm_layout = ImageLayout(
            axis_order=(ImageAxis.HEIGHT, ImageAxis.WIDTH, ImageAxis.CHANNELS),
            memory_order=MemoryOrder.COLUMN_MAJOR, # Different
            channels=ChannelFormat.RGB,
            directions={}
        )
        self.assertFalse(are_layouts_memory_equivalent(
            CommonLayouts.HWC_ROW_MAJOR_RGB,
            hwc_cm_layout
        ))


if __name__ == '__main__':
    unittest.main()
