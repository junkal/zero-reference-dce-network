# Low Light image enhancement using Zero-DCE network

This notebook implements the Zero-Reference Deep Curve Estimation (Zero-DCE), which formulates light enhancement as a task of image-specific curve estimation with a deep network. The method uses DCE-Net, a trained lightweight deep neural network that estimates pixel-wise and high-order curves for dynamic range adjustment of a given image.

Zero-DCE takes a low-light image as input and produces high-order tonal curves as its output. These curves are then used for pixel-wise adjustment on the dynamic range of the input to obtain an enhanced image. The curve estimation process is done in such a way that it maintains the range of the enhanced image and preserves the contrast of neighboring pixels.

* Original authors: Li, Chongyi and Guo, Chunle and Loy, Chen Change,
* Original paper: Learning to Enhance Low-Light Image via Zero-Reference Deep Curve Estimation
* Year published: 2021

**Reference**
1. [Zero-Reference Deep Curve Estimation for Low-Light Image Enhancement](https://arxiv.org/pdf/2001.06826.pdf)
2. [Keras implementation of Zero-DCE](https://keras.io/examples/vision/zero_dce/)

**DCE-Net model architecture**
![image](https://user-images.githubusercontent.com/6497242/137850019-70a4afc2-76c1-47aa-b427-889e4ccafdcc.png)

**Output Samples**
![image](https://user-images.githubusercontent.com/6497242/137850349-7a0be6c6-f4a9-4d73-81b3-2d3dbf42a9e2.png)

![image](https://user-images.githubusercontent.com/6497242/137850379-623a746d-3c9a-4c7b-83c5-f6f9490219db.png)

**Scripts for local inference**

python enhance.py -w "path to model weights" -i "path to input image" -o "output folder name: default to /output"

e.g., python enhance.py -w ./weights/model_last_weights.h5 -i ./lol_dataset/mytest/test-01.jpeg -o ./output_batch_1

**Scripts for Flask API service**
```
python server.py
```
The command here runs the server-side script to run the Flask app service and loads the Zero Reference DCE model and weights from /model folder.

1. Ensure the server.py is running, register username (--usr) and password (--pwd) to be used to authenticate subsequent API calls
```
python post_request.py login --usr david --pwd 123456
```
2. Post the image for inference using the client-side script to call the predict API. It sends the image file name and the image content encoded in base64. The image is defined by the -i argument and the image responses are stored at the folder defined by -o.
```
python post_request.py -i ./lol_dataset/mytest/test-01.jpeg -o responses login --usr david --pwd 123456

```
