import unittest
from pixel_canon.core import ImageLayout, ImageAxis, MemoryOrder, ChannelFormat, AxisDirection
from pixel_canon.common import CommonLayouts

class TestCoreComponents(unittest.TestCase):

    def test_imagelayout_creation(self):
        """Test that ImageLayout objects can be created successfully."""
        layout = ImageLayout(
            axis_order=(ImageAxis.HEIGHT, ImageAxis.WIDTH),
            memory_order=MemoryOrder.ROW_MAJOR,
            channels=ChannelFormat.LUMINANCE,
            directions={ImageAxis.HEIGHT: AxisDirection.DOWN}
        )
        self.assertIsInstance(layout, ImageLayout)
        self.assertEqual(len(layout.axis_order), 2)
        
    def test_imagelayout_is_hashable(self):
        """Test that ImageLayout can be used as a dictionary key."""
        layout1 = CommonLayouts.HWC_ROW_MAJOR_RGB
        layout2 = CommonLayouts.CHW_ROW_MAJOR_RGB
        
        my_dict = {layout1: "numpy-style", layout2: "pytorch-style"}
        
        self.assertEqual(my_dict[layout1], "numpy-style")
        self.assertEqual(my_dict[CommonLayouts.HWC_ROW_MAJOR_RGB], "numpy-style")
        
    def test_common_layouts_exist(self):
        """Test that common layouts are defined and are of the correct type."""
        self.assertIsInstance(CommonLayouts.HWC_ROW_MAJOR_RGB, ImageLayout)
        self.assertIsInstance(CommonLayouts.CHW_ROW_MAJOR_RGB, ImageLayout)
        self.assertIsInstance(CommonLayouts.HWC_ROW_MAJOR_RGBA_OPENGL, ImageLayout)
        self.assertIsInstance(CommonLayouts.CWH_COLUMN_MAJOR_RGB, ImageLayout)

    def test_channel_format_constants(self):
        """Test that ChannelFormat provides correct string constants."""
        self.assertEqual(ChannelFormat.RGB, "RGB")
        self.assertEqual(ChannelFormat.LUMINANCE, "LUMINANCE")

if __name__ == '__main__':
    unittest.main()
