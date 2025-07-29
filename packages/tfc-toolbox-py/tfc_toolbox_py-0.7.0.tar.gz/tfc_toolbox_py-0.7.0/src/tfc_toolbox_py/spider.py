import requests
from bs4 import BeautifulSoup


def get_xiaohongshu_article(note_id):
    """
    Get xiaohongshu's article.
    :param note_id: xiaohongshu's note id, you can get it from share link.
    :return: none
    """

    # configuration parameter
    base_url = "https://www.xiaohongshu.com/"
    article_url = base_url + 'explore/' + note_id

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Cookie': "abRequestId=8b30bb9c-2f3a-5427-9363-8273cdd3aab0; xsecappid=xhs-pc-web; a1=190807ce210fx3akmc3ql9vtrb1ikxp68iq997v9e50000971385; webId=8b6f487960b42513e6d748b8979da1ac; gid=yj8Y8Wf84WY8yj8Y8WSdJ3Why8iCq0T6SqA1Ajdjh9FDyj283TCUKj888jWyqY28D8YqiiSS; webBuild=4.25.1; web_session=040069b4c2785d678d4ec755a7344b22e9977a; unread={%22ub%22:%22668223a5000000001e013305%22%2C%22ue%22:%22667f272e000000001f0068e0%22%2C%22uc%22:25}; websectiga=8886be45f388a1ee7bf611a69f3e174cae48f1ea02c0f8ec3256031b8be9c7ee; sec_poison_id=713ab3f9-04b2-46bc-a8b0-3ef1dc2a0399; acw_tc=2a9731a22c64601a2ae0f0f92eefddfaba71eeb8576c9ca5928017173ced5e1e"
    }

    # 获取文章内容
    response = requests.get(url=article_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    # 使用find_all方法查找所有的meta标签
    meta_tags = soup.find_all("meta")

    # 遍历meta标签列表，并提取其content属性的值
    for meta in meta_tags:
        if meta.get("content") is not None and meta.get("name") is not None:
            match meta.get("name"):
                case "og:title": print("标题："+meta.get("content"))
                case "keywords": print("关键词："+meta.get("content"))
                case "description": print("描述："+meta.get("content"))
                case "og:xhs:note_comment": print("评论："+meta.get("content"))
                case "og:xhs:note_like": print("喜欢："+meta.get("content"))
                case "og:xhs:note_collect": print("收藏："+meta.get("content"))


def get_xiaohongshu_comment(note_id):
    """
    Get xiaohongshu's article comment.
    :param note_id: xiaohongshu's note id, you can get it from share link.
    :return: none
    """

    # configuration parameter
    comment_url = "https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id=" + note_id + "&cursor=&top_comment_id=&image_formats=jpg,webp,avif"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Cookie': "abRequestId=76f237d2-fcbb-5e1d-9fe4-c1dd11fb3d14; a1=1964ce0e88efp7cug36dbia0k83qslj1s19t1yz0550000203684; webId=bdbf795996515e33d51154f1d514ee4c; gid=yjK4Sd8ij2MWyjK4Sd8dYyvuYdiUWS7kqKfDj82308TYq928AM1Vyy888J8qKY48Y42DK0JS; web_session=040069b4c2785d678d4e7804363a4b8d2d29c0; acw_tc=0a00d1a617519577861218875e5733eb0ff6036d9c0ecab40fd3a246974628; webBuild=4.72.0; unread={%22ub%22:%2268634bca000000001c030d46%22%2C%22ue%22:%2268501360000000000f038bcb%22%2C%22uc%22:23}; websectiga=16f444b9ff5e3d7e258b5f7674489196303a0b160e16647c6c2b4dcb609f4134; sec_poison_id=8c748e9e-55af-45dd-9337-c5553ded46f5; xsecappid=ranchi; loadts=1751959542095"
    }

    # 发送GET请求并获取响应
    response = requests.get(url=comment_url, headers=headers)
    # 读取响应数据
    data = response.json()
    if data.get("success"):
        for comment in data.get("data").get("comments"):
            print("评论："+comment.get("content"))


def get_cqupt_schedule_text(id_num: str, week_num: int) -> None:
    """
    Input student id and week number, and get schedule text.
    :param id_num: Student ID number.
    :param week_num: Which week of this semester. If it is 0, you can get curriculum of all weeks.
    :return: None
    """

    # 课表查询网站
    base_url = "http://jwzx.cqupt.edu.cn/kebiao/kb_stu.php?xh="

    # 头部信息
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    }

    # 使用requests库发送GET请求
    response = requests.get(base_url + id_num, headers=headers)

    # 检查请求是否成功
    if response.status_code == 200:
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.content, "html.parser")

        # 查找含有特定class的table标签
        table_tags = soup.find_all('table')
        # 遍历table标签
        for table in table_tags:
            lesson = 0
            # 在table标签里面找tr标签
            tr_tags = table.find_all('tr')
            # 遍历所有找到的tr标签
            for tr in tr_tags:
                day = 0
                lesson += 1
                # 在tr标签中找所有td标签
                td_tags = tr.find_all("td")
                # 遍历所有td标签
                for td in td_tags:
                    day += 1
                    # 在所有td标签中找到所有div标签
                    div_tags = td.find_all("div", class_='kbTd')
                    # 打印所有div标签的内容
                    for div in div_tags:
                        week = 0
                        weekList = []
                        # 获取div标签的zc属性
                        zc_attribute = div.get('zc')
                        # 将zc属性转换为列表，并遍历
                        for item in list(zc_attribute):
                            week += 1
                            # 判断要查询的周数是否为0
                            if week_num != 0:
                                # 如果要查询的周数不为0，则只显示weekNum那一周的课表
                                if item != "0" and week == week_num:
                                    weekList.append(str(week))
                            elif week_num == 0:
                                # 如果要查询的周数为0，则显示所有周的课表
                                if item != "0":
                                    weekList.append(str(week))

                        lesson_name_record_tag = 0  # 课程名称记录标签
                        lesson_name_list = []  # 课程名称的字符串分解为字符后组成的列表
                        # 遍历div标签的文本，strip=True会移除前后的空白字符
                        for unit in div.get_text(strip=True):
                            # 设置标签为不向list添加内容
                            if unit == '地':
                                # 遇到字符“地”时，不向list添加内容
                                lesson_name_record_tag = 0
                            # 在标签为1时，向list添加内容
                            if lesson_name_record_tag == 1:
                                lesson_name_list.append(unit)
                            # 设置标签为向list添加内容
                            if unit == '-':
                                # 遇到字符“-”时，向list添加内容
                                lesson_name_record_tag = 1
                        # 将课程名称的字符串分解为字符后组成的列表转换成字符串
                        lesson_name_str = "".join(lesson_name_list)

                        # 在div标签中找font标签，确定一次课是几节课连上
                        font_tags = div.find_all("font")
                        # 遍历所有font标签，并获取font标签中的文本
                        for font in font_tags:
                            # 如果文本为空，则2节连上，如果文本第一个字符为“4”，则四节连上
                            lessonsNum = font.get_text()

                        # 课程不为空，则输出
                        if len(weekList) != 0:
                            print(f"第{",".join(weekList)}周，周{str(day - 1)}，", end="")
                            try:
                                # font标签中获得的字符串为“4节连上”
                                lessonsNum[0] == "4"
                                print(
                                    f"第{(lesson - 2) * 2 - 1}、{(lesson - 2) * 2}、{(lesson - 2) * 2 + 1}、{(lesson - 2) * 2 + 2}节")
                            except IndexError:
                                # font标签中获得的字符串为空，说明2节连上
                                print(f"第{(lesson - 1) * 2 - 1}、{(lesson - 1) * 2}节")
                            print(f"课程名称：{lesson_name_str}")
    else:
        print('Failed to retrieve the webpage.')
        print(f"StateCode:{response.status_code}")
