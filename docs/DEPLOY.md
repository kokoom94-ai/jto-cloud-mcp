# 운영자 배포 안내

직원 PC에 설치하는 절차가 아닙니다. 운영자가 한 번 온라인 서버를 배포하고 주소를 공유합니다.

## Render 체험 배포

저장소의 Deploy to Render 버튼 → Render 계정 로그인/가입 → 저장소 확인 → Blueprint 배포 순서입니다. 가입 약관 동의, GitHub 접근 승인, 요금제 선택은 계정 소유자가 화면을 확인합니다.

`render.yaml`의 `plan: free`는 무료 체험입니다. 유휴 후 최초 요청이 늦어 AI 연결이 시간 초과될 수 있습니다. 이때 서비스 홈페이지가 정상 열린 후 다시 연결하세요. 무료 서버의 파일시스템은 임시이며, 재시작 시 문서 데이터가 손실됩니다. 이 상태를 업무용 저장소로 사용하지 마세요.

## 업무용 지속 저장

`render.production.yaml`은 유료 전환을 검토할 때 사용할 별도 구성안입니다. 기본 `render.yaml`은 무료로 유지합니다. 2026-09-17 서비스 화면 기준 최소 컴퓨트는 월 $7이며, 1 GB 지속 디스크는 월 $0.25입니다. 기본 합계는 월 $7.25이고 세금 및 포함량 초과 트래픽/빌드 비용은 별도입니다. 비용 승인 전 이 구성은 적용하지 않습니다. [Render 요금](https://render.com/pricing)

기존 Blueprint 서비스는 승인 후 기존 `render.yaml`의 컴퓨트와 디스크 항목을 변경해 동기화합니다. 별도 Blueprint를 만들어 서비스를 중복 생성하지 마세요. 지속 디스크를 붙인 후에는 `/data` 쓰기, 재시작 전 생성 파일의 다운로드를 실제 확인해야 합니다. 이 검증 전에는 지속 저장 완료라고 표시하지 않습니다.

Render에서 유료 컴퓨트 및 지속 디스크 비용을 확인하고 선택합니다. 현재 공식 Blueprint 문서의 최소 유료 웹 인스턴스 식별자는 `0.5c-512mb`입니다. 설정 변경은 별도 요금 확인 후 진행합니다.

```yaml
plan: 0.5c-512mb
disk:
  name: jto-data
  mountPath: /data
  sizeGB: 1
```

단일 인스턴스만 운영하세요. 여러 인스턴스를 사용하려면 SQLite·로컬 디스크 대신 공유 데이터베이스와 객체 저장소가 필요합니다. 현재 코드에는 다중 인스턴스 저장소 구현이 포함되지 않습니다.

## 환경변수

| 이름 | 용도 |
|---|---|
| `JTO_PUBLIC_BASE_URL` | 서버의 외부 HTTPS origin. 경로를 붙이지 않음. Render에서는 생략하면 `RENDER_EXTERNAL_URL` 사용 |
| `JTO_AUTH_MODE` | 기본 public. 직원 공유용은 로그인·암호 없음 |
| `JTO_ACCESS_PASSWORD` | 선택적인 oauth 모드에서만 사용. public 모드에서는 읽어도 인증에 사용하지 않음 |
| `JTO_SIGNING_KEY` | 파일 링크 서명 키. Render 배포 시 자동 생성. 사용자에게 공유하지 않음 |
| `JTO_DATA_DIR` | 서버 데이터 경로. 기본 Blueprint는 `/data` |
| `JTO_DOWNLOAD_TTL_SECONDS` | 파일 링크 유효기간. 기본 86400초 |
| `PORT` | 호스팅 플랫폼의 수신 포트 |

선택적인 OAuth 모드에서만: 연결 암호 변경은 기존 OAuth 토큰을 즉시 취소하지 않습니다. 전체 연결을 철회하려면 유지보수 중 OAuth 저장 상태를 초기화하고 사용자에게 재연결을 안내해야 합니다. 서명 키를 변경하면 기존 다운로드 링크는 무효가 됩니다.

## 배포 완료 확인

1. `/health`에서 `status: ok`, `templates: 3` 확인.
2. `/.well-known/oauth-authorization-server`와 `/.well-known/oauth-protected-resource/mcp` 확인.
3. 실제 AI에서 인증 없음으로 등록 후 `jto_template_info` 호출.
4. 세 종류를 각각 생성하고 대화 링크로 파일 다운로드.
5. 한글에서 파일 열기·표지·본문·표·1PAGE 분량 확인.
6. 잘못된 서명과 만료 링크는 다운로드 거절되는지 확인.

공개 코드에 기본 암호·서명 키·생성 문서를 커밋하지 마세요. 호스팅 대시보드 로그가 요청 URL을 저장하면 다운로드 토큰이 기록될 수 있으므로 접근권한을 제한하세요. 앱 자체의 HTTP 접근 로그는 꺼져 있습니다.

참고: [Render Blueprint](https://render.com/docs/blueprint-spec), [배포 버튼](https://render.com/docs/deploy-to-render), [무료 서비스 제한](https://render.com/docs/free).
