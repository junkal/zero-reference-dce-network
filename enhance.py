import os
import argparse
import numpy as np
import tensorflow as tf
from pathlib import Path
from PIL import Image
from tensorflow import keras
from model.dce_model import ZeroDCE

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # get root directory
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))

def parse_opt(known=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('-weight', '-w', type = str, default = ROOT/'model/model_last_weights.h5', help='path to model weights')
    parser.add_argument('-image', '-i', type = str, required = True, help='file name of input image')
    parser.add_argument('-output', '-o', type = str, default = './output', help='file name of output image folder')
    return parser


def main(args=None):
    if os.name == 'posix':
        os.system('clear')
    else:
        # for windows platfrom
        os.system('cls')

    parser = parse_opt()
    args = parser.parse_args(args)
    print("[INFO] Input weights : {}".format(args.weight))
    print("[INFO] Input Image   : {}".format(args.image))
    print("[INFO] Output Folder : {}".format(args.output))

    ##load model weights
    zero_dce_model = ZeroDCE()
    zero_dce_model.load_weights(args.weight)
    print("[INFO] ZeroDCE model loaded")

    ## process image
    original_image = Image.open(args.image)
    original_image = keras.preprocessing.image.img_to_array(original_image)
    original_image = original_image.astype("float32") / 255.0
    original_image = np.expand_dims(original_image, axis=0)
    enhanced_image = zero_dce_model(original_image)
    enhanced_image = tf.cast((enhanced_image[0, :, :, :] * 255), dtype=np.uint8)
    enhanced_image = Image.fromarray(enhanced_image.numpy())

    ## infer image and save output
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    output_filename = os.path.basename(args.image)
    if args.output[-1] != '/':
        args.output = args.output + '/'

    enhanced_image.save(args.output + output_filename)
    print("[INFO] Image enhancement completed, output image saved at {}".format(args.output))

if __name__ == '__main__':
    main()
