# coding=utf-8
# /**
#  * Created by zhaoqp on 2017/1/10.
#  */
# function (a, b) {
#         for (var c = b.slice(32), d = [], e = 0; e < c.length; e++) {
#             var f = c.charCodeAt(e);
#             d[e] = f > 57 ? f - 87 : f - 48
#         }
#         c = 36 * d[0] + d[1];
#         var g = Math.round(a) + c;
#         b = b.slice(0, 32);
#         var h, i = [[], [], [], [], []], j = {}, k = 0;
#         e = 0;
#         for (var l = b.length; e < l; e++)h = b.charAt(e), j[h] || (j[h] = 1, i[k].push(h), k++, k = 5 == k ? 0 : k);
#         for (var m, n = g, o = 4, p = "", q = [1, 2, 5, 10, 50]; n > 0;)n - q[o] >= 0 ? (m = parseInt(Math.random() * i[o].length, 10), p += i[o][m], n -= q[o]) : (i.splice(o, 1), q.splice(o, 1), o -= 1);
#         return p
#     };
import PIL.Image as image

import requests

import ImageColor

import time

import random

def userresponse(a,b):

    c = b[32:]

    d = []

    for x in xrange(len(c)):

        y = ord(c[x])

        if y > 57:

            d.append(y-87)

        else:


            d.append(y-48)

    print 36 * d[0] + d[1]

    g = round(a)+(36 * d[0] + d[1])

    print g

    c = b[0:32]

    k = 0

    e = 0

    j = {}

    i = [[], [], [], [], []]

    for x in c:

        if j.get(x,None) is None:

            j[x] = 1

            i[k].append(x)

            k+=1

            if k == 5:

                k = 0

    n = g

    o = 4

    p = ""

    q = [1, 2, 5, 10, 50]




def pasteImage(im):

    b = "6_11_7_10_4_12_3_1_0_5_2_9_8".split("_")

    c = []

    for d in xrange(52):

        a = 2 * int(b[int(d % 26 / 2)]) + d % 2

        if int(d / 2) % 2 == 0:

            if d%2 == 0:

                a += 1

            else :

                a-=1

        if d< 26:

            a+=26

        else:

            a+=0

        c.append(a)
    rows = 2
    columns = 26
    sliceWidth = 10
    sliceHeight = 58
    new_im = image.new("RGB",(260,116))

    n = c

    im_list_upper = []
    im_list_down = []

    for row in xrange(rows):

        for column in xrange(columns):

            startingX = column * sliceWidth

            startingY = row * sliceHeight

            offsetX = n[row * columns + column] % 26 * 12 + 1

            if n[row * columns + column] > 25:

                offsetY = 116 / 2

                im_list_upper.append(im.crop((offsetX, 58, offsetX + 10, 116)))

            else:

                offsetY = 0

                im_list_down.append(im.crop((offsetX, 0, offsetX + 10, 58)))

    x_offset = 0
    for im in im_list_upper:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]
    x_offset = 0
    for im in im_list_down:
        new_im.paste(im, (x_offset, 58))
        x_offset += im.size[0]

    return new_im


def get_img(url):

    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"}

    img = requests.get(url,headers=headers)

    imge_file = url.split("/")[-1].replace(".webp",".jpg")

    with open(imge_file,"wb") as f:

        f.write(img.content)

        f.close()

    im = image.open(imge_file)

    return pasteImage(im)


def is_similar(image1,image2,x,y):
    pixel1=image1.getpixel((x,y))
    pixel2=image2.getpixel((x,y))
    for i in range(0,3):
        if abs(pixel1[i]-pixel2[i])>=60:
            return False
    return True


def get_diff_location(image1,image2):
    i=0
    for i in range(0,260):
        for j in range(0,116):
            if is_similar(image1,image2,i,j)==False:

                return  i,j


def get_id():

    #starttime

    o = int(1e4*random.random())+int(time.time()*1000)

    return o
    #endtime

    # int(time.time()*1000)

def get_track(length):
    '''
    根据缺口的位置模拟x轴移动的轨迹
    '''
    pass
    list=[]
#     间隔通过随机范围函数来获得
    x=random.randint(1,3)
    while length-x>=5:
        list.append(x)
        length=length-x
        x=random.randint(1,3)
    for i in xrange(length):
        list.append(1)
    return list


if __name__ == "__main__":

    bg = "http://static.geetest.com/pictures/gt/828603a60/828603a60.webp"

    fullbg = "http://static.geetest.com/pictures/gt/828603a60/bg/54182984.webp"

    bg_img = get_img(bg)

    fullbg_img = get_img(fullbg)

    x,y = get_diff_location(bg_img,fullbg_img)

    # move_distance = x-5
    #
    # print move_distance

    print get_track(x)

    # #print get_id()
    #
    # gt = "a1510c0b8b9f29926ea4827843616919ev"
    #
    # print userresponse(77,gt)

