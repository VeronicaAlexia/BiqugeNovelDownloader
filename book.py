import threading
import BiquPavilionAPI
from instance import *


class Book:

    def __init__(self, book_info: dict, index=None):
        self.index = index
        self.progress_bar = 1
        self.save_book_dir = None
        self.config_book_dir = None
        self.chapter_info_list = list()
        self.threading_pool = list()
        self.download_chapter_list = list()
        self.cover_url = book_info.get('Img')
        self.book_name = book_info.get('Name')
        self.book_tag = book_info.get('CName')
        self.book_intro = book_info.get('Desc')
        self.author_name = book_info.get('Author')
        self.book_updated = book_info.get('LastTime')
        self.book_state = book_info.get('BookStatus')
        self.book_id = novel_id_url(book_info.get('Id'))
        self.last_chapter = del_title(book_info.get('LastChapter'))
        self.pool_sema = threading.BoundedSemaphore(Vars.cfg.data.get('threading_pool_size'))

    def show_book_info(self) -> str:
        show_info = '作者:{0:<{2}}状态:{1}\n'.format(self.author_name, self.book_state, isCN(self.author_name))
        show_info += '最新:{0:<{2}}更新:{1}\n'.format(self.last_chapter, self.book_updated, isCN(self.last_chapter))
        self.config_book_dir = os.path.join(Vars.cfg.data.get('config_book'), self.book_name)
        self.save_book_dir = os.path.join(Vars.cfg.data.get('save_book'), self.book_name, f'{self.book_name}.txt')
        write(self.save_book_dir, 'w', '{}简介:\n{}'.format(show_info, self.arrange(self.book_intro)))
        makedirs(self.config_book_dir)
        return show_info

    def progress(self, length: int) -> None:
        self.progress_bar += 1
        percentage = (self.progress_bar / length) * 100
        print('{}/{} 进度:{:^3.0f}%'.format(self.progress_bar, length, percentage), end='\r')

    def customized_content(self, volume_name: str, title: str, content: str, new_content: str = "") -> str:
        if title != "该章节未审核通过" and "正在更新中，请稍等片刻，内容更新后" not in content:
            for line in content.splitlines():
                content_line = line.strip().strip("　")
                if content_line != "":
                    new_content += f"\n　　{content_line}"
            return "{}: {}\n{}".format(volume_name, self.del_nbsp(title), new_content)
        return ""

    def arrange(self, intro: str, new_intro: str = "", width: int = 60) -> str:
        for line in intro.splitlines():
            intro_line = line.strip().strip("　")
            if intro_line != "":
                new_intro += "\n" + intro_line[:width]
        return new_intro

    def del_nbsp(self, text: str) -> str:
        return text.replace("&nbsp;", '').replace('&nbsp', '')

    def download_content_threading(self, volume_name, chapter_info, download_length) -> None:
        self.pool_sema.acquire()
        content_info = BiquPavilionAPI.Chapter.content(self.book_id, chapter_info.get('id'))
        content = self.customized_content(volume_name, chapter_info.get('name'), content_info.get('content'))
        if content != "" and content != "\n":
            write("{}/{}.txt".format(self.config_book_dir, content_info.get('cid')), 'w', content)
        self.progress(download_length)
        self.pool_sema.release()

    def output_text_and_epub(self) -> None:
        for chapter_index, info in enumerate(self.chapter_info_list):  # 获取目录文,并且 遍历文件名
            if os.path.exists(os.path.join(self.config_book_dir, str(info.get('id')) + ".txt")):
                content = write(os.path.join(self.config_book_dir, str(info.get('id')) + ".txt"), 'r').read()
                Vars.epub_info.add_chapter(info.get('id'), self.del_nbsp(info.get('name')), content, chapter_index)
                write(self.save_book_dir, 'a', "\n\n\n" + content)

        Vars.epub_info.save(), self.chapter_info_list.clear(), self.download_chapter_list.clear()

    def get_chapter_api(self) -> int:
        filename_list = os.listdir(self.config_book_dir)
        for index, catalogue_info in enumerate(BiquPavilionAPI.Book.catalogue(self.book_id), start=1):
            print(f"第{index}卷", catalogue_info.get('name'))
            for info in catalogue_info.get('list'):
                self.chapter_info_list.append(info)
                if str(info.get('id')) + ".txt" in filename_list:
                    continue
                self.download_chapter_list.append([catalogue_info.get('name'), info])
        return len(self.download_chapter_list)

    def download_chapter_threading(self):
        length = self.get_chapter_api()
        if length == 0:
            print("没有需要下载的章节！")
            return length
        for volume_name, chapter_info in self.download_chapter_list:
            self.threading_pool.append(
                threading.Thread(target=self.download_content_threading, args=(volume_name, chapter_info, length,))
            )
        for thread in self.threading_pool:
            thread.start()

        for thread in self.threading_pool:
            thread.join()
        self.threading_pool.clear()
