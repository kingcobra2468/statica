from distutils import dir_util
import filecmp
import os

from pytest import fixture

from statica.file.decoder import FileDecoder


@fixture
def data_path(tmp_path, request):
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)
    dir_util.copy_tree(str(test_dir), str(tmp_path))

    return tmp_path


def test_file_decode(data_path):
    encoded_image_path = str(data_path / 'image_encoded.mp4')
    output_image_file = str(data_path / 'image.png')
    gen_output_image_file = str(data_path / 'gen_image.png')

    file_encoder = FileDecoder(
        encoded_image_path, gen_output_image_file, buffer_size=100)
    file_encoder.decode()

    assert filecmp.cmp(output_image_file, gen_output_image_file)


def test_file_decode_h264(data_path):
    encoded_image_path = str(data_path / 'image_encoded_h264.mp4')
    output_image_file = str(data_path / 'image.png')
    gen_output_image_file = str(data_path / 'gen_image.png')

    file_encoder = FileDecoder(
        encoded_image_path, gen_output_image_file, buffer_size=100)
    file_encoder.decode()

    assert filecmp.cmp(output_image_file, gen_output_image_file)
