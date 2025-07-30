"""The implementation of using 'https://github.com/cszn/BSRGAN' to enhance MR/CT images.
"""

import os.path
from dataclasses import dataclass
import numpy as np
import torch
from .utils.singleton import Singleton
from .utils.logging import logger
from numpy import ndarray

from .models.bsrgan_network_rrdbnet import RRDBNet as net
from .models.esrgan_network_rrdbnet import RRDBNet as esrgan_net
from .utils.utils_image import (imread_uint, imresize_np, imsave,
                                tensor2uint,  uint2tensor4)


@dataclass
class BaseSRGanWrapper(metaclass=Singleton):

    # model_name (_type_, optional): Represent the pre-trained model name.
    model_path: str
    # net_scale (int, optional): Represent the net-scale value. Defaults to 2.
    net_scale: int = 2

    def __post_init__(self):

        if not self.model_path:
            raise FileNotFoundError(f'Invalid model name: {self.model_path}')

        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')

        print('cuda' if torch.cuda.is_available() else 'cpu')

        self.load_model()

    def load_model(self, model_path: str = None):
        if not model_path:
            # use the default model path if not specified
            model_path = self.model_path

        if not os.path.isfile(model_path):
            # raise error if the model file is not found
            raise FileNotFoundError(f'Not found model file: {model_path}')

        logger.debug(f'Loading model from {model_path}')
        loadnet = torch.load(
            model_path, map_location=torch.device('cpu'), weights_only=True)

        if 'params_ema' in loadnet:
            self.model = esrgan_net(scale=self.net_scale)
            # involving 'realESRGan Model'
            self.model.load_state_dict(loadnet['params_ema'], strict=True)
        else:
            self.model = net(sf=self.net_scale)
            self.model.load_state_dict(loadnet, strict=True)

        self.model.eval()
        self.model.to(self.device)
        torch.cuda.empty_cache()

    def predict(self, image: ndarray, max_value: int, scale: float = 0.5):

        # reformat input image (single channel image) into 3-dimensions
        if (image_dim := image.ndim) == 2:
            image = np.stack((image,)*3, axis=-1)

        image = uint2tensor4(image, max_value)
        image = image.to(self.device)

        with torch.no_grad():
            output_img = self.model(image)

        output_img = tensor2uint(output_img, max_value)

        if (scale := scale/self.net_scale) != 1:
            output_img = imresize_np(output_img, scale=scale)

        return output_img[:, :, 0] if image_dim == 2 else output_img


class BSRGan(BaseSRGanWrapper):
    def __init__(self, model_path: str, net_scale: int = 2):
        super().__init__(model_path=model_path, net_scale=net_scale)


class RealESRGan(BaseSRGanWrapper):
    def __init__(self, model_path: str, net_scale: int = 2):
        super().__init__(model_path=model_path, net_scale=net_scale)


# def bsrgan_predict(source: str, output: str, model_path: str, max_value:int, scale: int = 2):
#     image = imread_uint(source, n_channels=3)
#     output_img = BSRGan(model_path=model_path).predict(
#         image=image, max_value=max_value, scale=scale)
#     imsave(output_img, output or image)


# def realesrgan_predict(source: str, output: str, model_path: str, max_value:int, scale: int = 2):
#     image = imread_uint(source, n_channels=3)
#     output_img = RealESRGan(model_path=model_path).predict(
#         image=image, max_value=max_value, scale=scale)
#     imsave(output_img, output or image)
