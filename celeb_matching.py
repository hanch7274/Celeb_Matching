import argparse
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw
import requests
import json
import re
client_id = ""
client_secret = ""

def parse_filename(filename):
    return re.match(".*\\\\{1,2}(.*)\.jpg",filename).group(1)

def check_jpg(filename):
    result = re.match(".*jpg$",filename)
    if result:
        return True
    else:
        return False


def detect_face(face_file, max_results=4):
    client = vision.ImageAnnotatorClient()
    content = face_file.read()
    image = types.Image(content=content)

    return client.face_detection(image=image, max_results=max_results).face_annotations

def crop_faces(image,filename):
    num=1
    faces = detect_face(image,4)
    json_data = []
    filename = parse_filename(filename)
    for face in faces:
        im = Image.open(image)
        box = [(vertex.x,vertex.y) for vertex in face.bounding_poly.vertices]
        area = (box[0][0], box[0][1], box[1][0], box[2][1])
        croped_im = im.crop(area)
        croped_im.save('output_{}{}.jpg'.format(filename, num), "JPEG")
        json_data.append(detect_celebrity('output_{}{}.jpg'.format(filename,num)))
        num = num + 1
    return json_data, num-1

def detect_celebrity(file_name):
    url = "https://openapi.naver.com/v1/vision/celebrity"  # 유명인 얼굴 비교 API
    files = {'image': open(file_name,'rb')}
    headers = {'X-Naver-Client-Id': client_id, 'X-Naver-Client-Secret': client_secret}
    response = requests.post(url, files=files, headers = headers)
    rescode = response.status_code
    if(rescode==200):
        return json.loads(response.text)
    else:
        print("Error Code:" + rescode)
        return 0

def show_result(data,num):
    print_logo()
    print("사진 분석 결과\n=======================================================")
    for i in range(len(num)):
        for index, face_data in enumerate(data[i]["faces"]):
            print("얼굴{} -> {}를 {}%만큼 닮았습니다.".format(i, face_data["celebrity"]["value"],
                int(round(float(face_data["celebrity"]["confidence"]), 2) * 100)))

def print_logo():
    logo = """
 _______       _        _        _______                  _     _
(_______)     | |      | |      (_______)        _       | |   (_)
 _       _____| | _____| |__     _  _  _ _____ _| |_ ____| |__  _ ____   ____
| |     | ___ | || ___ |  _ \   | ||_|| (____ (_   _) ___)  _ \| |  _ \ / _  |
| |_____| ____| || ____| |_) )  | |   | / ___ | | |( (___| | | | | | | ( (_| |
 \______)_____)\_)_____)____/   |_|   |_\_____|  \__)____)_| |_|_|_| |_|\___ |
                                                                       (_____|
                                                        Made By Chang Hyeon Han
                                         Using Google Vision API, Naver CFR API

    ================================================================================
                                                                              """
    print(logo)
def main(input_filename):
    if check_jpg(input_filename):
        with open(input_filename, 'rb') as image:
            json_data, num_of_faces = crop_faces(image,input_filename)
            show_result(json_data, num_of_faces)
    else:
        print("jpg 이미지 파일을 삽입하세요")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image_file', help='The image you\'d like to crop.')
    args = parser.parse_args()
    parser = argparse.ArgumentParser()
    main(args.image_file)