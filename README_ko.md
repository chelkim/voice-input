# 음성 입력 / Voice Input

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Platform-Ubuntu](https://img.shields.io/badge/Platform-Ubuntu-orange.svg)](https://ubuntu.com/)
[![Tested_on-Ubuntu_24.04](https://img.shields.io/badge/Tested_on-Ubuntu_24.04-24.04-orange.svg)](https://ubuntu.com/)

[English](README.md) | [中文](README_zh.md) | [한국어](README_ko.md)

---

음성 입력은 Linux 시스템을 위한 전역 단축키 기반 음성 받아쓰기 도구입니다. `Alt+Q` 또는 `Alt+W`를 누르기만 하면 녹음이 시작되고, 시스템이 자동으로 음성을 텍스트로 변환하여 현재 포커스된 입력 필드에 붙여넣습니다. 중국어, 영어, 일본어, 한국어, 광둥어 등 여러 언어를 지원하며, 중국어 인식 정확도가 가장 높습니다. UI 언어는 사용자의 말하기 습관에 따라 자동으로 전환됩니다. X11 및 Wayland 데스크톱 세션 모두 완벽 지원, 시스템 부팅 시 자동 시작, 네트워크 불필요, 오프라인 작동.

## 기능

- **이중 단축키** - `Alt+Q` (자동 Enter) 또는 `Alt+W` (수동 Enter)
- **다국어 지원** - 중국어, 영어, 일본어, 한국어, 광둥어 자동 인식
- **스마트 UI 언어** - 말하는 습관에 맞춰 UI가 자동으로 전환
- **이중 플랫폼** - X11 및 Wayland 세션 완벽 지원
- **실시간 음량 표시** - 녹음 중 음량 파형 애니메이션 표시
- **자동 붙여넣기** - 인식 후 텍스트를 포커스된 창에 자동으로 붙여넣기
- **녹음 취소** - 녹음 중 `ESC`를 눌러 취소
- **자동 시작** - 시스템 부팅 시 자동 시작
- **오프라인** - 네트워크 불필요, 모든 처리 로컬에서 수행

## 시스템 요구사항

- **운영 체제**: Ubuntu 24.04 LTS (테스트 완료)
  - 다른 Ubuntu 버전은 작동할 수 있지만 공식적으로 테스트되지 않음
  - **macOS 및 Windows는 테스트되지 않음** - 기능이 보장되지 않음
- **데스크톱 환경**: GNOME (자동 시작 지원)
- **세션 유형**: X11 또는 Wayland
- **하드웨어**: 음성 입력을 위한 마이크 필요
- **Python**: 3.8 이상

### 필수 의존성

이 프로그램에는 다음 도구가 필요합니다:

| 도구 | 용도 | 설치 명령 |
|------|------|---------|
| xdotool | 창 포커스 감지, 키보드 시뮬레이션 | `sudo apt install xdotool` |
| xsel | 클립보드 작업 | `sudo apt install xsel` |
| xprop | 창 클래스 감지 | `sudo apt install x11-utils` |

Wayland 추가 필요:

| 도구 | 용도 | 설치 명령 |
|------|------|---------|
| ydotoold | Wayland 키보드 시뮬레이션 | `sudo apt install ydotool` |
| wl-copy | Wayland 클립보드 | `sudo apt install wl-clipboard` |

### 창 호환성

프로그램이 창 유형을 자동으로 감지하여 적절한 붙여넣기 방법을 선택합니다:

**터미널 창** (`Ctrl+Shift+V` 사용):
- GNOME Terminal
- Konsole
- xterm, uxterm
- Terminator
- Alacritty
- Kitty
- Tilix
- Terminology
- LilyTerm
- Termite

**GUI 애플리케이션** (`Ctrl+V` 사용):
- 모든 그래픽 애플리케이션 (gedit, VS Code, Chrome, Firefox 등)
- Electron 앱
- Qt 애플리케이션
- GTK 애플리케이션

이 자동 감지 기능은 음성 입력이 터미널과 그래픽 환경 모두에서 올바르게 작동하도록 합니다.

## 빠른 시작

### 설치

```bash
git clone https://github.com/chelkim/voice-input.git ~/.voice-input
cd ~/.voice-input
./setup.sh
```

### 사용 방법

1. 데몬이 실행 중인지 확인 (부팅 시 자동 시작)
2. 대상 입력 필드 클릭
3. `Alt+Q` (자동 Enter) 또는 `Alt+W` (수동 Enter)를 눌러 녹음 시작
4. 말하기
5. 다시 `Alt+Q` 또는 `Alt+W`를 눌러 녹음 중지
6. 텍스트가 입력 필드에 자동으로 붙여넣어짐
   - `Alt+Q` 사용: 붙여넣기 후 Enter 자동 누름
   - `Alt+W` 사용: 붙여넣기 후 Enter 안 누름 (수동)
7. 녹음 중 `ESC`를 눌러 취소

## 설정

설정 파일: `~/.config/voice-input/config`

```ini
[hotkey]
# 수정 키 + 주 키. 수정 키: ctrl, alt, shift, meta
# Alt+Q: 자동 Enter 모드 (붙여넣기 후 Enter 자동 누름)
# Alt+W: 수동 Enter 모드 (붙여넣기 후 Enter 안 누름)
key = Alt+Q
key2 = Alt+W

[recognition]
# 언어: auto (자동 감지), zh (중국어), en (영어), ja (일본어), ko (한국어), yue (광둥어)
# 참고: 중국어 인식 정확도가 가장 높습니다. 다른 언어는 정확도가 낮을 수 있습니다.
language = auto

[ui]
# UI 표시 언어: auto (사용량 기반 자동 감지), zh, en, ja, ko, yue
# auto로 설정하면 시스템이 사용자의 언어 선호도를 학습하고 그에 따라 UI를 전환합니다
language = auto
```

**언어 인식 정확도 참고:**

SenseVoice 모델은 6개 언어를 지원하지만 인식 정확도가 다릅니다:
- **중국어 (zh)** - 가장 높은 정확도, 가장 많은 학습 데이터
- **영어 (en)** - 좋은 정확도
- **일본어 (ja), 한국어 (ko), 광둥어 (yue)** - 낮은 정확도, 중국어와 혼동될 수 있음

최상의 결과를 얻으려면 `language = auto`를 유지하는 것이 좋습니다. 주로 중국어를 사용하는 경우 모델이 자동으로 중국어 인식을 우선시합니다.

**스마트 UI 언어 기능:**
- `[ui] language = auto`일 때 시스템이 사용자의 말하기 패턴을 자동으로 감지합니다
- 동일한 언어로 2번 연속 전사하면 UI 언어가 자동으로 업데이트됩니다
- 예: 중국어를 2번 연속 말하면 UI가 중국어 표시로 전환됩니다
- 언어 통계가 영구적으로 저장되어 데몬 재시작 후에도 유지됩니다

설정 수정 후 데몬을 재시작해야 합니다.

## 일반적인 명령

```bash
# 데몬 재시작
pkill -f daemon.py && sleep 1 && ~/.voice-input/venv-voice/bin/python3 ~/.voice-input/src/daemon.py &

# 데몬 상태 확인
pgrep -f daemon.py

# 로그 보기
tail -f ~/.voice-input/voice.log
```

## 개발

### 프로젝트 구조

모듈식 아키텍처로 유지보수 및 확장이 용이합니다:

- **src/config.py** - 설정 관리
- **src/platform/** - 플랫폼 추상화 레이어
- **src/keyboard/** - 키보드 캡처
- **src/audio/** - 오디오 녹음
- **src/recognition/** - 음성 인식
- **src/ui/** - 사용자 인터페이스

### 테스트 실행

```bash
./venv-voice/bin/python3 tests/test_config.py
```

## Wayland 설정

Wayland에는 추가 설정이 필요합니다:

```bash
# ydotoold 설치
sudo apt-get install ydotoold

# /dev/uinput 권한 설정
sudo chmod 666 /dev/uinput

# ydotoold 시작
ydotoold &
```

## 문제 해결

### 데몬이 응답하지 않음

```bash
pgrep -f daemon.py  # 실행 중인지 확인
~/.voice-input/venv-voice/bin/python3 ~/.voice-input/src/daemon.py &  # 수동 시작
```

### Wayland에서 ydotool이 작동하지 않음

1. ydotoold가 실행 중인지 확인: `ps aux | grep ydotoold`
2. /dev/uinput 권한 확인: `ls -la /dev/uinput`

### 터미널에 붙여넣기 불가

터미널은 `Ctrl+Shift+V`를 사용하여 붙여넣기합니다

이 프로그램은 대상 창이 터미널인지 자동으로 감지하여 적절한 붙여넣기 단축키(`Ctrl+Shift+V`는 터미널용, `Ctrl+V`는 GUI 애플리케이션용)를 사용합니다.

## 기여

개발 지침은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

## 라이선스

MIT 라이선스 - [LICENSE](LICENSE) 파일을 참조하세요.
