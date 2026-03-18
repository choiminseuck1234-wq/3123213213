import sys
import zipfile
import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QMessageBox


class HWPXMerger(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HWPX 병합 프로그램")
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        self.btn_select = QPushButton("HWPX 파일 선택")
        self.btn_select.clicked.connect(self.select_files)

        self.btn_merge = QPushButton("병합 실행")
        self.btn_merge.clicked.connect(self.merge_files)

        layout.addWidget(self.btn_select)
        layout.addWidget(self.btn_merge)

        self.setLayout(layout)

        self.files = []

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "파일 선택", "", "HWPX Files (*.hwpx)")
        if files:
            self.files = files
            QMessageBox.information(self, "선택 완료", f"{len(files)}개 파일 선택됨")

    def unzip_hwpx(self, file, extract_path):
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

    def merge_files(self):
        if not self.files:
            QMessageBox.warning(self, "오류", "파일을 먼저 선택하세요")
            return

        temp_dirs = []

        try:
            # 첫 파일 기준
            base_dir = "temp_base"
            self.unzip_hwpx(self.files[0], base_dir)

            section_path = os.path.join(base_dir, "Contents", "section0.xml")

            with open(section_path, "r", encoding="utf-8") as f:
                base_content = f.read()

            insert_pos = base_content.rfind("</hp:body>")

            merged_body = ""

            # 나머지 파일 이어붙이기
            for i, file in enumerate(self.files[1:], start=1):
                temp_dir = f"temp_{i}"
                temp_dirs.append(temp_dir)

                self.unzip_hwpx(file, temp_dir)

                sec_path = os.path.join(temp_dir, "Contents", "section0.xml")

                with open(sec_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # body 안쪽만 추출
                start = content.find("<hp:body>")
                end = content.find("</hp:body>")

                if start != -1 and end != -1:
                    merged_body += content[start + 9:end]

            # 병합
            new_content = (
                base_content[:insert_pos]
                + merged_body
                + base_content[insert_pos:]
            )

            with open(section_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            # 결과 저장
            save_path, _ = QFileDialog.getSaveFileName(self, "저장", "merged.hwpx", "HWPX Files (*.hwpx)")
            if not save_path:
                return

            shutil.make_archive("merged", 'zip', base_dir)
            os.rename("merged.zip", save_path)

            QMessageBox.information(self, "완료", "병합 완료!")

        finally:
            # temp 삭제
            shutil.rmtree(base_dir, ignore_errors=True)
            for d in temp_dirs:
                shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HWPXMerger()
    window.show()
    sys.exit(app.exec_())
