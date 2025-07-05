import mimetypes
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


class GoogleDriveManager:
    def __init__(self, service_account_file, parent_folder_id=None):
        self.service_account_file = service_account_file
        self.parent_folder_id = parent_folder_id
        self.scopes = ['https://www.googleapis.com/auth/drive']
        self.service = self._authenticate()

    def _authenticate(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file, scopes=self.scopes
        )
        return build('drive', 'v3', credentials=credentials)

    def create_folder(self, folder_name):
        metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if self.parent_folder_id:
            metadata['parents'] = [self.parent_folder_id]

        folder = self.service.files().create(body=metadata, fields='id').execute()
        print("✅ Folder created:", folder['id'])
        return folder['id']

    def get_or_create_folder(self, folder_name):
        folders = self.search_by_name(folder_name, mime_type='application/vnd.google-apps.folder')
        if folders:
            print("📁 Folder already exists:", folders[0]['id'])
            return folders[0]['id']
        else:
            return self.create_folder(folder_name)

    def create_nested_folders(self, folder_names_list, parent_folder_id=None):
        parent = self.parent_folder_id
        if parent_folder_id:
            parent = parent_folder_id
        for folder_name in folder_names_list:
            folder_id = None
            existing_folders = self.search_by_name(folder_name, mime_type='application/vnd.google-apps.folder')
            for f in existing_folders:
                if parent and f.get('parents', [None])[0] == parent:
                    folder_id = f['id']
                    break

            if not folder_id:
                metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent] if parent else []
                }
                folder = self.service.files().create(body=metadata, fields='id').execute()
                folder_id = folder['id']
                print("📁 Created nested folder:", folder_name, "| ID:", folder_id)

            parent = folder_id
        return parent

    def share_folder(self, folder_id, email, role='writer', notify=True):
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
        self.service.permissions().create(
            fileId=folder_id,
            body=permission,
            fields='id',
            sendNotificationEmail=notify
        ).execute()
        print("✅ Folder shared with", email)

    def upload_file_old(self, file_name, file_path, mime_type='application/octet-stream', folder_id=None):
        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(file_path, mimetype=mime_type)
        uploaded_file = self.service.files().create(
            body=file_metadata, media_body=media, fields='id'
        ).execute()
        print("✅ File uploaded:", uploaded_file['id'])
        return uploaded_file['id']

    def upload_file(self, file_name, file_path, mime_type=None, folder_id=None):
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'

        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(file_path, mimetype=mime_type)
        uploaded_file = self.service.files().create(
            body=file_metadata, media_body=media, fields='id'
        ).execute()
        print("✅ File uploaded:", uploaded_file['id'])
        return uploaded_file['id']

    def list_files_in_folder(self, folder_id):
        query = "'{}' in parents and trashed = false".format(folder_id)
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        print("📂 Files in folder:")
        for f in files:
            print("- {} ({})".format(f['name'], f['id']))
        return files

    def search_by_name(self, name, mime_type=None):
        query = "name='{}' and trashed = false".format(name)
        if mime_type:
            query += " and mimeType='{}'".format(mime_type)

        results = self.service.files().list(q=query, fields="files(id, name, mimeType, parents)").execute()
        return results.get('files', [])

    def delete_file_or_folder(self, file_id):
        try:
            self.service.files().delete(fileId=file_id).execute()
            print("🗑️ Deleted:", file_id)
        except HttpError as e:
            print("❌ Error deleting file:", e)

    def get_file_info(self, file_id):
        try:
            file = self.service.files().get(fileId=file_id, fields='id, name, mimeType, createdTime').execute()
            print("📄 File Info:", file)
            return file
        except HttpError as e:
            print("❌ Error retrieving file info:", e)
            return None

    def download_file(self, file_id, destination_path):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(destination_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print("⬇️ Download progress: {:.0%}".format(status.progress()))
        print("✅ File downloaded to:", destination_path)

    def rename_file_or_folder(self, file_id, new_name):
        file_metadata = {'name': new_name}
        updated = self.service.files().update(fileId=file_id, body=file_metadata).execute()
        print("✏️ Renamed to:", updated['name'])
        return updated

    def move_file_to_folder(self, file_id, new_parent_id):
        file = self.service.files().get(fileId=file_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents', []))

        updated_file = self.service.files().update(
            fileId=file_id,
            addParents=new_parent_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()
        print("📂 Moved file to new folder.")
        return updated_file


if __name__ == '__main__':
    manager = GoogleDriveManager('googleapi.json', parent_folder_id='1Af9oruqcXuE6b37DwdArG5v3mUusDhoc')

    # 1. Create and share folder
    folder_id = manager.get_or_create_folder('Upload Folder')
    manager.share_folder(folder_id, 'shishir.siam01@gmail.com')

    # 2. Upload different file types
    # manager.upload_file('photo.jpg', 'Files/photo.jpg', folder_id=folder_id)
    # manager.upload_file('docs_file.docx', 'Files/docs_file.docx', folder_id=folder_id)
    # manager.upload_file('audio.mp3', 'Files/mp3_file.mp3', folder_id=folder_id)
    # manager.upload_file('pdf_file.pdf', 'Files/pdf_file.pdf', folder_id=folder_id)
    # manager.upload_file('zip_file.zip', 'Files/zip_file.zip', folder_id=folder_id)
    # manager.upload_file('html_file.html', 'Files/html_file.html', folder_id=folder_id)

    # 3. List files
    manager.list_files_in_folder(folder_id)

    # 4. Get file info
    manager.get_file_info(folder_id)

    # 5. Optional: Rename file
    # manager.rename_file_or_folder('<file_id>', 'renamed_file.pdf')

    # 6. Optional: Download file
    # manager.download_file('<file_id>', 'downloads/file.pdf')

    # 7. Optional: Move file
    # manager.move_file_to_folder('<file_id>', '<another_folder_id>')

    # 8. Optional: Create nested folders like /2025/July/05
    nested_id = manager.create_nested_folders(['2025', 'July', '05'], parent_folder_id=folder_id)

    # 9. Optional: Delete file or folder
    # manager.delete_file_or_folder('<file_id>')

    # 10. Optional: Search for files by name
    # manager.search_by_name('file_name', 'application/pdf')

    # 11. Optional: Search for folders by name
    # manager.search_by_name('folder_name', 'application/vnd.google-apps.folder')
