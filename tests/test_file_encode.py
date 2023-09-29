from distutils import dir_util
import filecmp
import os

from pytest import fixture

from statica.file.encoder import FileEncoder


@fixture
def data_path(tmp_path, request):
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)
    dir_util.copy_tree(str(test_dir), str(tmp_path))

    return tmp_path


def test_file_encode(data_path):
    input_image_file = str(data_path / 'image.png')
    encoded_image_path = str(data_path / 'image_encoded.mp4')
    gen_encoded_image_path = str(data_path / 'gen_image_encoded.mp4')

    file_encoder = FileEncoder(input_image_file, gen_encoded_image_path)
    file_encoder.encode(False)

    assert filecmp.cmp(encoded_image_path, gen_encoded_image_path)


def test_file_encode_h264(data_path):
    input_image_file = str(data_path / 'image.png')
    encoded_image_path = str(data_path / 'image_encoded_h264.mp4')
    gen_encoded_image_path = 'gen_image_encoded_h264.mp4'

    file_encoder = FileEncoder(input_image_file, gen_encoded_image_path)
    file_encoder.encode(True)

    assert filecmp.cmp(encoded_image_path, gen_encoded_image_path)
