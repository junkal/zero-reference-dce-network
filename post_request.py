import io
import os
import requests
import base64
import argparse
from PIL import Image

def parse_opt(known=False):
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", type = str, default=None, help="path to image to send processing")
    parser.add_argument("-o", "--output", type= str, default='responses', help="output folder to store return images")
    parser.add_argument("-ip", type = str, default='127.0.0.1:4000', help="ip address:port of service")

    subparsers = parser.add_subparsers(dest='subcommand')
    praser_register = subparsers.add_parser("register")
    praser_register.add_argument('--usr',type = str, required=True, help='user name to register with')
    praser_register.add_argument('--pwd',type = str, required=True, help='password to register with')

    praser_login = subparsers.add_parser("login")
    praser_login.add_argument("--usr",type = str, required=True, help='user name to log in with')
    praser_login.add_argument("--pwd",type = str, required=True, help='password to log in with')

    return parser

def check_resize(image):
    width, height = image.size
    if width > 1028 or height > 1028:
        print("[INFO] Input image has size larger than 1028, resize to 1028 with aspect ratio")
        image.thumbnail((1028, 1028), Image.ANTIALIAS)

    byteIO = io.BytesIO()
    image.save(byteIO, format='JPEG')
    image = byteIO.getvalue()

    return image

def register_user(username, password, url):
    login_credential = {'username': str(username), 'password': str(password)}

    response = requests.post(url + 'register', json = login_credential)

    if response.status_code != 200:
        print("[Error] register_user: {}".format(response.reason))
        return False
    else:
        print("[INFO] register_user: {}".format(response.json()))
        return True

def login_user(username, password, url):

    login_info = bytes(username+":"+password, 'utf-8')

    response = requests.get(url+"login", headers = {"Authorization": "Basic {}".format(base64.b64encode(login_info).decode("utf8"))})
    os.environ["API_KEY"] = str(response.json()["token"])

    if response.status_code != 200:
        print ("[Error] login_user: {}".format(response.reason))
        return False
    else:
        print("[INFO] login_user message: {}".format(response.json()["message"]))
        return True

def predict_image(image, output_folder, url):
    # load the input image and construct the payload for the request
    filename = os.path.basename(image)
    file_ext = os.path.splitext(filename)[1]

    if file_ext in ['.jpg', '.png', '.jpeg']:
        image = Image.open(image, mode = 'r')
        image = check_resize(image)
        payload = {"filename": filename, "image": image}

        headers = {'X-Access-Tokens': os.environ["API_KEY"]}

        # submit the request
        response = requests.post(url+"predict", headers = headers, files=payload)

        if response.status_code == 200:
            # ensure the request was sucessful
            data = response.json()
            print("[INFO] POST successful, success:{}, data_size:{} - time taken {}s"
                .format(data["success"], data["size"], response.elapsed))

            filename = os.path.splitext(data['filename'])[0] + '_output.jpeg'
            image = data['image']

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            with open(os.path.join(output_folder, filename), "wb") as fh:
                fh.write(base64.b64decode(image))
        else:
            print("[ERROR] POST not successful, status {} reason {}".format(response.status_code, response.reason))

    else:
        print("[ERROR] Unacceptable image file extension {}".format(file_ext))

def main(args = None):
    parser = parse_opt()
    args = parser.parse_args(args)

    URL = "http://" + args.ip + "//"

    if args.subcommand == "register":
        print("[INFO] Register user username: {} password: {}".format(args.usr, args.pwd, URL))
        if register_user(args.usr, args.pwd, URL):
            print("[INFO] user {} registered successfully".format(args.usr))
        exit(0)

    if args.subcommand == "login":
        print("[INFO] Login user username: {} password: {}".format(args.usr, args.pwd, URL))
        if not login_user(args.usr, args.pwd, URL):
            exit(0)

    if args.image != None:
        predict_image(args.image, args.output, URL)
    else:
        print("[ERROR] No input image defined")

if __name__ == '__main__':
    main()
