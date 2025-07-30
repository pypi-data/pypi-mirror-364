import os
import warnings
from typing import Optional, Union

from simba.mixins.config_reader import ConfigReader
from simba.mixins.image_mixin import ImageMixin
from simba.mixins.pop_up_mixin import PopUpMixin
from simba.roi_tools.roi_ui_mixin import ROI_mixin
from simba.utils.checks import (check_file_exist_and_readable,
                                check_if_dir_exists)
from simba.utils.enums import ROI_SETTINGS
from simba.utils.errors import InvalidInputError
from simba.utils.read_write import (find_all_videos_in_directory, get_fn_ext,
                                    get_video_meta_data)

warnings.filterwarnings("ignore")


WINDOW_SIZE = (775, 900)

class ROI_ui(ROI_mixin, ConfigReader):

    """
    Main antry-point for drawing ROIs on videos.

    ..note::
      See ROI tutorial on `GitHub <https://github.com/sgoldenlab/simba/blob/master/docs/roi_tutorial_new_2025.md>`_ or `ReadTheDocs https://simba-uw-tf-dev.readthedocs.io/en/latest/tutorials_rst/roi_tutorial_new_2025.html>`_

    :example:
    >>> ROI_ui(config_path=r"C:\troubleshooting\mouse_open_field\project_folder\project_config.ini", video_path=r"C:\troubleshooting\mouse_open_field\project_folder\videos\Video1.mp4")
    >>> ROI_ui(config_path=r"/mnt/c/troubleshooting/mouse_open_field/project_folder/project_config.ini", video_path=r"/mnt/c/troubleshooting/mouse_open_field/project_folder/videos/Video1.mp4")

    """
    def __init__(self,
                 video_path: Union[str, os.PathLike],
                 config_path: Optional[Union[str, os.PathLike]] = None,
                 roi_coordinates_path: Optional[Union[str, os.PathLike]] = None,
                 video_dir: Optional[Union[str, os.PathLike]] = None):

        check_file_exist_and_readable(file_path=video_path)
        if config_path is None:
            if (video_dir is None) and (roi_coordinates_path is None):
                raise InvalidInputError(msg='If not passing a config path, then pass roi_coordinates_path and video_dir', source=self.__class__.__name__)
        if config_path is not None:
            ConfigReader.__init__(self, config_path=config_path, read_video_info=False, create_logger=False)
            check_file_exist_and_readable(file_path=config_path)
        if roi_coordinates_path is not None:
            self.roi_coordinates_path = roi_coordinates_path
            check_if_dir_exists(in_dir=video_dir)
            self.video_dir = video_dir
        self.video_meta =  get_video_meta_data(video_path=video_path, fps_as_int=False)
        self.video_ext = get_fn_ext(filepath=video_path)[2][1:]
        self.img, self.img_idx = ImageMixin.find_first_non_uniform_clr_frm(video_path=video_path)
        self.define_ui = PopUpMixin(title="REGION OF INTEREST (ROI) SETTINGS", size=WINDOW_SIZE, icon='shapes_small')
        ROI_mixin.__init__(self, video_path=video_path, config_path=config_path, img_idx=self.img_idx, main_frm=self.define_ui.root, roi_coordinates_path=self.roi_coordinates_path)
        self.other_project_video_paths = find_all_videos_in_directory(directory=self.video_dir, as_dict=True).values()
        self.other_project_video_paths = [x for x in self.other_project_video_paths if x != video_path]
        self.other_project_video_names = [get_fn_ext(x)[1] for x in self.other_project_video_paths]
        self.settings = {item.name: item.value for item in ROI_SETTINGS}
        self.get_video_info_panel(parent_frame=self.define_ui.main_frm, row_idx=0)
        self.get_select_img_panel(parent_frame=self.define_ui.main_frm, row_idx=1)
        self.get_select_shape_type_panel(parent_frame=self.define_ui.main_frm, row_idx=2)
        self.get_shape_attr_panel(parent_frame=self.define_ui.main_frm, row_idx=3)
        self.get_shape_name_panel(parent_frame=self.define_ui.main_frm, row_idx=4)
        self.get_interact_panel(parent_frame=self.define_ui.main_frm, row_idx=5, top_level=self.define_ui.root)
        self.get_draw_panel(parent_frame=self.define_ui.main_frm, row_idx=6, top_level=self.define_ui.root)
        self.get_shapes_from_other_video_panel(parent_frame=self.define_ui.main_frm, row_idx=7)
        self.get_save_roi_panel(parent_frame=self.define_ui.main_frm, row_idx=8)
        self.get_status_bar_panel(parent_frame=self.define_ui.main_frm, row_idx=9)
        self.get_file_menu(root=self.define_ui.root)
        self.set_selected_shape_type(shape_type='rectangle')
        self.define_ui.root.protocol("WM_DELETE_WINDOW", self._close)
        self.define_ui.main_frm.mainloop()

    def _close(self):
        try:
            self.close_img()
        except:
            pass
        self.define_ui.root.destroy()
        self.define_ui.root.quit()

#ROI_ui(config_path=r"C:\troubleshooting\mitra\project_folder\project_config.ini", video_path=r"C:\troubleshooting\mitra\project_folder\videos\501_MA142_Gi_CNO_0514.mp4")

# ROI_ui(config_path=r"C:\troubleshooting\mouse_open_field\project_folder\project_config.ini",
#        video_path=r'C:\troubleshooting\mouse_open_field\project_folder\videos\Video2.mp4')

# ROI_ui(config_path=None,
#        video_path=r'C:\troubleshooting\mouse_open_field\project_folder\videos\Video2.mp4',
#        roi_coordinates_path=r"C:\troubleshooting\mitra\project_folder\logs\measures\ROI_definitions.h5",
#        video_dir=r"C:\troubleshooting\mitra\test")

# ROI_ui(config_path=r"C:\troubleshooting\mitra\project_folder\project_config.ini",
#        video_path=r"C:\troubleshooting\mitra\project_folder\videos\501_MA142_Gi_CNO_0514.mp4")