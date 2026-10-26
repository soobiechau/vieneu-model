"""Tải giọng AI VieNeu-TTS v3 Turbo (bản int8 chạy CPU) từ HuggingFace về PC rồi gói thành MỘT file ~330 MB
để tải lên GitHub Releases. Học viên dùng skill trên điện thoại (Claude AI chặn HuggingFace, cho tải GitHub) sẽ lấy model từ đó.

Chạy bằng DONG-GOI-VIENEU.bat (nhấp đúp). Cần Python + mạng thường (PC không bị chặn HuggingFace).
Ra thư mục VIENEU-GITHUB/ cạnh file này: vieneu-v3-turbo-int8.tar + sha256.txt + HUONG-DAN.txt.

Giấy phép: VieNeu-TTS v3 Turbo = Apache-2.0 (giọng có sẵn + âm thanh tạo ra được dùng thương mại, theo model card);
codec MOSS-Audio-Tokenizer-Nano = OpenMOSS. Giữ file GIAY-PHEP.txt trong gói khi phát lại.
"""
import hashlib, subprocess, sys, tarfile, shutil
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TM = Path(__file__).resolve().parent
RA = TM / 'VIENEU-GITHUB'
TEN = 'vieneu-v3-turbo-int8'
VIENEU = 'pnnbao-ump/VieNeu-TTS-v3-Turbo'
CODEC = 'OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX'
# (repo, file trên repo, thư mục trong gói)
FILES = [(VIENEU, f'onnx_int8/{f}', 'onnx_int8') for f in (
            'config.json', 'tokenizer.json', 'vieneu_prefill.onnx', 'vieneu_decode_step.onnx',
            'vieneu_acoustic_cached.onnx', 'vieneu_backbone_shared.data', 'vieneu_v3_heads.npz')] + \
        [(VIENEU, f, 'root') for f in ('config.json', 'speaker_encoder.onnx', 'denoiser.onnx', 'README.md')] + \
        [(CODEC, f, 'codec') for f in (
            'codec_browser_onnx_meta.json', 'moss_audio_tokenizer_decode_full.onnx',
            'moss_audio_tokenizer_decode_shared.data', 'moss_audio_tokenizer_decode_step.onnx',
            'moss_audio_tokenizer_encode.onnx', 'moss_audio_tokenizer_encode.data', 'README.md')]
GIAY_PHEP = ('VieNeu-TTS v3 Turbo - https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo - Apache License 2.0 '
             '(tac gia Pham Nguyen Ngoc Bao). Nhan ban giong: chi dung giong ban co quyen su dung.\n'
             'MOSS-Audio-Tokenizer-Nano-ONNX - https://huggingface.co/OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX - '
             'xem README.md trong thu muc codec/.\n'
             'Ban goi lai nguyen ven, khong sua file model.\n')


def main():
    try:
        from huggingface_hub import hf_hub_download
    except Exception:
        print('Cài huggingface_hub…')
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'huggingface_hub'], check=False)
        from huggingface_hub import hf_hub_download
    shutil.rmtree(RA, ignore_errors=True); RA.mkdir()
    tar_p = RA / f'{TEN}.tar'
    with tarfile.open(tar_p, 'w', format=tarfile.PAX_FORMAT) as t:
        for i, (repo, fn, dich) in enumerate(FILES, 1):
            print(f'[{i}/{len(FILES)}] tải {repo}/{fn}', flush=True)
            p = Path(hf_hub_download(repo, fn))
            t.add(str(p.resolve()), arcname=f'{TEN}/{dich}/{Path(fn).name}')
        gp = RA / 'GIAY-PHEP.txt'; gp.write_text(GIAY_PHEP, encoding='utf-8')
        t.add(str(gp), arcname=f'{TEN}/GIAY-PHEP.txt')
    h = hashlib.sha256()
    with open(tar_p, 'rb') as f:
        for b in iter(lambda: f.read(8 << 20), b''):
            h.update(b)
    mb = tar_p.stat().st_size / 1048576
    (RA / 'sha256.txt').write_text(h.hexdigest(), encoding='utf-8')
    (RA / 'HUONG-DAN.txt').write_text(
        f'Giọng AI VieNeu: {TEN}.tar · {mb:.0f} MB · sha256 = {h.hexdigest()}\n\n'
        '1. Vào github.com (đăng nhập) → New repository → đặt tên vd. vieneu-model → chọn PUBLIC → Create.\n'
        '2. Trong repo: Releases → Create a new release → tag: v1 → kéo thả file vieneu-v3-turbo-int8.tar vào → Publish release.\n'
        '3. Bấm chuột phải vào file vừa tải lên trong trang release → Copy link. Link có dạng\n'
        '   https://github.com/<ten-ban>/vieneu-model/releases/download/v1/vieneu-v3-turbo-int8.tar\n'
        '4. Gửi link đó (và mã sha256 ở trên) cho Claude: Claude điền vào skill (assets/vieneu-model.json) và đóng gói lại.\n'
        'Mô tả release nên ghi: "Bản sao VieNeu-TTS v3 Turbo (Apache-2.0) của pnnbao-ump, cho skill quảng cáo shop".\n',
        encoding='utf-8')
    print(f'\nXONG: {tar_p}  ({mb:.0f} MB)\nsha256: {h.hexdigest()}\nĐọc {RA / "HUONG-DAN.txt"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
