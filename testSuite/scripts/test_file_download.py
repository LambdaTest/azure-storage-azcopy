import os
import shutil
import time
import unittest
import utility as util

class FileShare_Download_User_Scenario(unittest.TestCase):

    # test_upload_download_1kb_file_wildcard_all_files verifies the upload/download of 1Kb file with wildcard using azcopy.
    def test_upload_download_1kb_file_wildcard_all_files(self):
        # create file of size 1KB.
        filename = "test_upload_download_1kb_file_wildcard_all_files.txt"
        file_path = util.create_test_file(filename, 1024)

        wildcard_path = file_path.replace(filename, "*")

        # Upload 1KB file using azcopy.
        result = util.Command("copy").add_arguments(wildcard_path).add_arguments(util.test_share_url). \
            add_flags("log-level", "info").execute_azcopy_copy_command()
        self.assertTrue(result)

        # Verifying the uploaded file.
        # the resource local path should be the first argument for the azcopy validator.
        # the resource sas should be the second argument for azcopy validator.
        resource_url = util.get_resource_sas_from_share(filename)
        result = util.Command("testFile").add_arguments(file_path).add_arguments(resource_url).execute_azcopy_verify()
        self.assertTrue(result)

        # downloading the uploaded file
        src = util.get_resource_sas_from_share(filename)
        src_wildcard = util.get_resource_sas_from_share("*")
        dest = util.test_directory_path + "/test_upload_download_1kb_file_wildcard_all_files_dir"
        try:
            if os.path.exists(dest) and os.path.isdir(dest):
                shutil.rmtree(dest)
        except:
            self.fail('error removing directory ' + dest)
        finally:
            os.makedirs(dest)

        result = util.Command("copy").add_arguments(src_wildcard).add_arguments(dest). \
            add_flags("log-level", "info").add_flags("include-pattern", filename.replace("wildcard", "*")). \
            execute_azcopy_copy_command()
        self.assertTrue(result)

        # Verifying the downloaded file
        result = util.Command("testFile").add_arguments(os.path.join(dest, filename)).add_arguments(
            src).execute_azcopy_verify()
        self.assertTrue(result)

    # test_upload_download_1kb_file_fullname verifies the upload/download of 1Kb file with wildcard using azcopy.
    def test_upload_download_1kb_file_wildcard_several_files(self):
        # create file of size 1KB.
        filename = "test_upload_download_1kb_file_wildcard_several_files.txt"
        prefix = "test_upload_download_1kb_file_wildcard_several*"
        file_path = util.create_test_file(filename, 1024)

        wildcardSrc = file_path.replace(filename, prefix)
        # Upload 1KB file using azcopy.
        result = util.Command("copy").add_arguments(wildcardSrc).add_arguments(util.test_share_url). \
            add_flags("log-level", "info").execute_azcopy_copy_command()
        self.assertTrue(result)

        # Verifying the uploaded file.
        # the resource local path should be the first argument for the azcopy validator.
        # the resource sas should be the second argument for azcopy validator.
        resource_url = util.get_resource_sas_from_share(filename)
        result = util.Command("testFile").add_arguments(file_path).add_arguments(resource_url).execute_azcopy_verify()
        self.assertTrue(result)

        # downloading the uploaded file
        src = util.get_resource_sas_from_share(filename)
        wildcardSrc = util.get_resource_sas_from_share(prefix)
        dest = util.test_directory_path + "/test_upload_download_1kb_file_wildcard_several_files"
        try:
            if os.path.exists(dest) and os.path.isdir(dest):
                shutil.rmtree(dest)
        except:
            self.fail('error removing directory ' + dest)
        finally:
            os.makedirs(dest)

        result = util.Command("copy").add_arguments(src).add_arguments(dest).add_flags("include-pattern", prefix). \
            add_flags("log-level", "info").execute_azcopy_copy_command()
        self.assertTrue(result)

        # Verifying the downloaded file
        result = util.Command("testFile").add_arguments(os.path.join(dest, filename)).add_arguments(
            src).execute_azcopy_verify()
        self.assertTrue(result)

    # util_test_n_1kb_file_in_dir_upload_download_azure_directory verifies the upload of n 1kb file to the share.
    def util_test_n_1kb_file_in_dir_upload_download_azure_directory(self, number_of_files, recursive):
        # create dir dir_n_files and 1 kb files inside the dir.
        dir_name = "util_test_n_1kb_file_in_dir_upload_download_azure_directory_" + recursive + "_" + str(
            number_of_files) + "_files"
        sub_dir_name = "dir_subdir_" + str(number_of_files) + "_files"

        # create n test files in dir
        src_dir = util.create_test_n_files(1024, number_of_files, dir_name)

        # create n test files in subdir, subdir is contained in dir
        util.create_test_n_files(1024, number_of_files, os.path.join(dir_name, sub_dir_name))

        # prepare destination directory.
        # TODO: note azcopy v2 currently only support existing directory and share.
        dest_azure_dir_name = "dest azure_dir_name"
        dest_azure_dir = util.get_resource_sas_from_share(dest_azure_dir_name)

        result = util.Command("create").add_arguments(dest_azure_dir).add_flags("serviceType", "File"). \
            add_flags("resourceType", "Bucket").execute_azcopy_create()
        self.assertTrue(result)

        # execute azcopy command
        result = util.Command("copy").add_arguments(src_dir).add_arguments(dest_azure_dir). \
            add_flags("recursive", recursive).add_flags("log-level", "debug").execute_azcopy_copy_command()
        self.assertTrue(result)

        # execute the validator.
        dest_azure_dir_to_compare = util.get_resource_sas_from_share(dest_azure_dir_name + "/" + dir_name)
        result = util.Command("testFile").add_arguments(src_dir).add_arguments(dest_azure_dir_to_compare). \
            add_flags("is-object-dir", "true").add_flags("is-recursive", recursive).execute_azcopy_verify()
        self.assertTrue(result)

        download_azure_src_dir = dest_azure_dir_to_compare
        download_local_dest_dir = src_dir + "_download"

        try:
            if os.path.exists(download_local_dest_dir) and os.path.isdir(download_local_dest_dir):
                shutil.rmtree(download_local_dest_dir)
        except:
            print("catch error for removing " + download_local_dest_dir)
        finally:
            os.makedirs(download_local_dest_dir)

        # downloading the directory created from azure file directory through azcopy with recursive flag to true.
        result = util.Command("copy").add_arguments(download_azure_src_dir).add_arguments(
            download_local_dest_dir).add_flags("log-level", "debug"). \
            add_flags("recursive", recursive).execute_azcopy_copy_command()
        self.assertTrue(result)

        # verify downloaded file.
        # todo: ensure the comparing here
        result = util.Command("testFile").add_arguments(os.path.join(download_local_dest_dir, dir_name)).add_arguments(
            download_azure_src_dir). \
            add_flags("is-object-dir", "true").add_flags("is-recursive", recursive).execute_azcopy_verify()
        self.assertTrue(result)

    def test_3_1kb_file_in_dir_upload_download_azure_directory_recursive(self):
        self.util_test_n_1kb_file_in_dir_upload_download_azure_directory(3, "true")

