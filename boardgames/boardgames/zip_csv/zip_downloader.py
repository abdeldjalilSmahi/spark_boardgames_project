import os
import zipfile
import requests
import re


class ZipDownloader:
    def __init__(self, url="https://geek-export-stats.s3.amazonaws.com/boardgames_export/boardgames_ranks_2024-03-03"
                           ".zip?X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz"
                           "-Credential=AKIAJYFNCT7FKCE4O6TA%2F20240303%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date"
                           "=20240303T201325Z&X-Amz-SignedHeaders=host&X-Amz-Expires=600&X-Amz-Signature"
                           "=6b6bbe254cffd1796f1adc6a4e8b8df7b354ff69614e8b3ceb3cc124f2a2cad2"):
        self.url = url

    def download(self):
        match = re.search(r'/([^/]+\.zip)\?', self.url)
        file_name = match.group(1) if match else None
        file_path = f"../data/{file_name}"
        response = requests.get(self.url)
        final_file_path = "../data/boardgames_ranks.zip"
        with open(file_path, "wb") as file:
            file.write(response.content)

        os.rename(file_path, final_file_path)
        print(f"Le fichier a été téléchargé et renommé sous : {final_file_path}")

    @staticmethod
    def unzip_file(path="../data/boardgames_ranks.zip", extract_to="../data/"):
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            extracted_files = os.listdir(extract_to)
            print("Fichiers extraits :", extracted_files)

# if __name__ == "__main__":
#     url = ("https://geek-export-stats.s3.amazonaws.com/boardgames_export/boardgames_ranks_2024-03-03.zip?X-Amz-Content"
#            "-Sha256=UNSIGNED-PAYLOAD&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJYFNCT7FKCE4O6TA"
#            "%2F20240303%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20240303T191053Z&X-Amz-SignedHeaders=host&X-Amz"
#            "-Expires=600&X-Amz-Signature=1b53a5f4c6e5f52439767f35392bba3a565ee337b2cf8cf7b3abb846ad01fec5")
#
#     zipfile_downloader = ZipDownloader(url)
#     zipfile_downloader.download()
#     zipfile_downloader.unzip_file()
