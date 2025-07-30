# LogSentinelAI Package Migration Guide

## pip 라이브러리로 전환 완료

이 프로젝트는 uv 기반의 현대적인 Python 패키지로 완전히 전환되었습니다.

### 📦 새로운 패키지 구조

```
LogSentinelAI/
├── src/logsentinelai/           # 메인 패키지
│   ├── __init__.py             # 패키지 진입점
│   ├── cli.py                  # CLI 인터페이스
│   ├── analyzers/              # 로그 분석기들
│   │   ├── httpd_access.py     # HTTP 액세스 로그 분석
│   │   ├── httpd_apache.py     # Apache 에러 로그 분석
│   │   ├── linux_system.py     # 리눅스 시스템 로그 분석
│   │   └── tcpdump_packet.py   # TCPDump 패킷 분석
│   ├── core/                   # 핵심 기능
│   │   ├── commons.py          # 공통 유틸리티
│   │   └── prompts.py          # LLM 프롬프트 템플릿
│   ├── config/                 # 설정 관리
│   │   └── settings.py         # 설정 처리
│   └── utils/                  # 유틸리티
│       └── geoip_downloader.py # GeoIP 데이터베이스 다운로더
├── pyproject.toml              # 패키지 정의 및 의존성
├── uv.lock                     # 의존성 잠금 파일
└── README.md                   # 업데이트된 문서
```

### 🚀 새로운 설치 방법

#### 개발 설치 (추천)
```bash
# uv 설치 (아직 없다면)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 프로젝트 클론 및 설치
git clone https://github.com/call518/LogSentinelAI.git
cd LogSentinelAI
uv pip install --editable .
```

#### 일반 설치
```bash
# 소스에서 직접 설치
pip install git+https://github.com/call518/LogSentinelAI.git

# 또는 로컬 클론에서
git clone https://github.com/call518/LogSentinelAI.git
cd LogSentinelAI
pip install .
```

### ✨ 새로운 명령어

기존의 `python analysis-*.py` 스크립트들이 편리한 CLI 명령어로 대체되었습니다:

| 기존 방식 | 새로운 방식 |
|----------|-----------|
| `python analysis-httpd-access-log.py` | `logsentinelai-httpd-access` |
| `python analysis-httpd-apache-log.py` | `logsentinelai-httpd-apache` |
| `python analysis-linux-system-log.py` | `logsentinelai-linux-system` |
| `python analysis-tcpdump-packet.py` | `logsentinelai-tcpdump` |
| `python download_geoip_database.py` | `logsentinelai-geoip-download` |

### 📋 사용 예제

```bash
# 기본 도움말
logsentinelai --help

# HTTP 액세스 로그 분석
logsentinelai-httpd-access --log-path /var/log/apache2/access.log

# 실시간 모니터링
logsentinelai-linux-system --mode realtime

# SSH 원격 분석
logsentinelai-tcpdump --remote --ssh admin@server.com --ssh-key ~/.ssh/id_rsa

# GeoIP 데이터베이스 다운로드
logsentinelai-geoip-download
```

### 🔧 프로그래밍 인터페이스

패키지를 Python 코드에서도 사용할 수 있습니다:

```python
import logsentinelai

# LLM 모델 초기화
model = logsentinelai.initialize_llm_model()

# 분석 설정 가져오기
config = logsentinelai.get_analysis_config("httpd_access")

# 배치 분석 실행
logsentinelai.run_generic_batch_analysis(
    log_type="httpd_access",
    analysis_schema_class=HTTPDAccessAnalysis,
    prompt_template=PROMPT_TEMPLATE,
    analysis_title="Custom Analysis"
)
```

### 🎯 변경사항 요약

1. **패키지화**: 모든 코드가 `logsentinelai` 패키지로 구조화
2. **CLI 통합**: 일관된 명령어 인터페이스 제공
3. **의존성 관리**: `pyproject.toml`과 `uv.lock`으로 현대적 의존성 관리
4. **확장성**: 새로운 분석기를 쉽게 추가할 수 있는 구조
5. **호환성**: 기존 기능과 설정 파일들은 그대로 유지

### 📖 마이그레이션 가이드

기존 사용자들을 위한 마이그레이션 단계:

1. **설치**: 새로운 패키지 설치
   ```bash
   cd LogSentinelAI
   uv pip install --editable .
   ```

2. **설정 유지**: 기존 `config` 파일은 그대로 사용 가능

3. **명령어 변경**: 스크립트 호출을 새로운 CLI 명령어로 변경

4. **테스트**: 새로운 명령어들이 정상 작동하는지 확인
   ```bash
   logsentinelai-httpd-access --help
   ```

### 🚀 향후 계획

- PyPI 패키지 등록으로 `pip install logsentinelai` 지원
- Docker 이미지 업데이트
- 추가 분석기 플러그인 시스템
- 웹 인터페이스 통합

---

**🎉 이제 LogSentinelAI는 현대적인 Python 패키지로 더욱 사용하기 쉬워졌습니다!**
