# ChatGPT · Claude · Gemini 연결

확인 기준일: 2026-09-17. 앱의 메뉴·계정 조건은 바뀔 수 있습니다. 아래는 공식 문서를 기준으로 한 연결 안내이며 실제 세 앱 시험 완료 선언이 아닙니다.

공유할 MCP 주소: **https://jto-cloud-mcp.onrender.com/mcp**

안내 페이지: https://jto-cloud-mcp.onrender.com/

## 공통

운영자가 배포한 HTTPS 서버의 `/mcp` 주소가 필요합니다. GitHub 저장소 주소를 MCP 서버 URL 칸에 넣지 마세요. 최초 OAuth 승인 화면에 운영자의 연결 암호를 입력합니다. 암호는 AI 대화에 보내지 마세요.

서버는 Streamable HTTP·OAuth 검색·동적 클라이언트 등록·PKCE를 지원합니다. 파일은 HTTPS 링크와 MCP `resource_link`를 함께 반환합니다. 앱마다 링크/첨부 카드 표시가 달라 동일한 모양은 보장하지 않습니다.

## ChatGPT

1. ChatGPT의 플러그인/앱 관리 화면을 엽니다. 공식 연결 문서에서 안내하는 추가(+) 버튼을 선택합니다. 계정에 따라 설정 → 앱 → 만들기 또는 개발 연결 메뉴가 표시될 수 있습니다.
2. 이름은 `JTO 문서 도구`, 설명은 `제주관광공사 사업계획·결과보고·1PAGE 양식 문서 생성`으로 입력합니다.
3. 공개 서버 주소에 `https://jto-cloud-mcp.onrender.com/mcp`를 입력합니다.
4. 인증을 선택하는 화면에서는 OAuth를 선택합니다. 고급 Client ID/Secret은 이 서버의 동적 등록을 사용할 때 직접 입력하지 않습니다.
5. JTO 인증 화면에 운영자가 전달한 연결 암호를 입력합니다. 암호를 대화창에 쓰지 않습니다.
6. 연결된 도구 목록에서 `jto_template_info`, `jto_generate_document` 등을 확인합니다.
7. 새 대화의 도구 메뉴에서 JTO 연결을 선택하고 아래 확인 문장을 요청합니다.

조직 계정은 관리자의 맞춤 앱/개발 연결 권한이 필요할 수 있습니다. 메뉴가 없으면 계정 정책부터 확인해야 하며, URL을 대화창에 붙이는 것만으로 등록되지는 않습니다.

공개 앱 디렉터리 등록은 별도 심사 절차입니다. 이 저장소를 공개해도 디렉터리에 자동 등록되지는 않습니다.

[OpenAI MCP 서버 문서](https://developers.openai.com/plugins/build/mcp-server) · [연결·시험](https://developers.openai.com/plugins/deploy/connect-chatgpt)

## Claude

1. Customize → Connectors → + → Add custom connector를 엽니다.
2. 이름 `JTO 문서 도구`, 서버 URL `https://jto-cloud-mcp.onrender.com/mcp`를 입력하고 Add를 누릅니다.
3. Connect를 누르고 JTO 인증 화면에서 연결 암호를 입력합니다. 고급 OAuth Client ID/Secret은 기본적으로 비워 둡니다.
4. 대화 입력창의 + → Connectors에서 JTO를 켭니다.
5. 아래 확인 문장을 요청하고 생성된 링크를 눌러 파일을 받습니다.

Team/Enterprise는 조직 관리자가 Organization settings → Connectors에서 먼저 등록해야 할 수 있습니다. Claude는 원격 서버를 클라우드에서 호출하므로 사용자 PC를 켜둘 필요가 없습니다.

[Anthropic 공식 연결 안내](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)

## Gemini

공식 도움말에서 확인한 현재 맞춤 앱 연결 조건은 **미국, 18세 이상, 개인 Google 계정, Keep Activity 켜짐, 영어 지원**입니다. 한국 사용자/조직 계정에서 바로 사용할 수 있다고 보장하지 않습니다.

1. 지원되는 계정으로 Gemini 웹에 로그인합니다.
2. Settings → Connected Apps를 엽니다. 보이지 않으면 Personal Intelligence → Connected Apps를 확인합니다.
3. Custom apps → Add a custom app에 `https://jto-cloud-mcp.onrender.com/mcp`를 입력합니다.
4. Next를 누르고 JTO 연결 암호로 인증을 완료합니다. 이 서버는 동적 클라이언트 등록을 지원하므로 고급 자격증명을 수동 입력하는 방식은 기본 절차가 아닙니다.
5. 대화에서 `@`를 입력해 JTO 앱을 선택하고 아래 확인 문장을 요청합니다.

웹에서 연결하면 지원되는 모바일 앱에서도 사용할 수 있다고 안내되어 있습니다. Google의 Spark 전체 제공 지역 확대 공지와 맞춤 앱 기능의 구체적인 제공 조건은 다를 수 있으므로, 실제 계정에 Custom apps 메뉴가 있는지 확인합니다. 한국 계정에서 연결 완료를 보장하지 않습니다.

Gemini API/CLI의 MCP 사용과 일반 Gemini 앱 연결은 별도입니다. API/CLI 테스트를 일반 대화창 호환 시험으로 대신하지 않습니다. 지원 지역을 우회하는 방법은 이 배포 절차에 포함하지 않습니다.

[Google 공식 맞춤 앱 연결 안내](https://support.google.com/gemini/answer/17209137?co=GENIE.Platform%3DDesktop&hl=en-TZ)

## 동료에게 공유할 내용

“이 서비스는 JTO 사업계획·결과보고·1PAGE 양식으로 문서를 생성합니다. 아래 MCP 주소를 AI의 맞춤 커넥터 설정에 등록하고 연결을 승인하세요. 연결 후 ‘2027 중화권 마케팅 사업계획을 작성해줘’ 또는 ‘이 내용을 1PAGE로 만들어줘’라고 요청하면 대화에서 다운로드 링크를 받을 수 있습니다.”

MCP 주소는 `https://jto-cloud-mcp.onrender.com/mcp`입니다. GitHub 주소는 소스·설치 안내용으로 함께 공유할 수 있습니다. 연결 암호는 운영자가 사용을 허용한 사람에게 별도로 전달합니다. GitHub나 공개 안내에는 암호를 올리지 않습니다.

## 최초 연결 확인 및 요청 예시

- 연결 확인: `JTO 도구의 jto_template_info를 실제 호출해서 사업계획·결과보고·1PAGE 세 양식이 있는지 확인해줘.`
- 사업계획: `2027 중화권 마케팅 사업계획을 JTO 사업계획 양식으로 작성하고 HWPX 파일 다운로드 링크를 줘. 제안 예산은 제안값으로 표시하고 확인되지 않은 정보는 구분해줘.`
- 결과보고: `첨부한 실제 실적으로 JTO 결과보고 양식의 HWPX를 만들어줘. 없는 실적이나 집행액은 만들어내지 마.`
- 1PAGE: `이 내용을 JTO 1PAGE 양식으로 요약하고 HWP 파일 링크를 줘.`

정상 연결의 기준은 AI가 말로 성공했다고 답하는 것이 아니라 실제 도구 호출 결과와 서버 다운로드 링크가 반환되는 것입니다. 링크를 열었을 때 파일이 내려받아지고 한글에서 정상 열리는지 확인합니다.

## 오류 해결

- 브라우저에서 `/mcp`를 직접 열 때 `Authentication required`: 미인증 요청이므로 정상입니다. 안내 페이지는 `/`입니다.
- AI에서 인증 후 같은 오류: JTO 연결을 끊고 다시 인증합니다. 무료 서버 재시작으로 연결 정보가 사라졌을 수 있습니다.
- 첫 연결 시간 초과: 무료 서비스가 잠들어 있을 수 있습니다. 안내 페이지가 열린 뒤 다시 연결합니다.
- 다운로드 404: 만료, 서버 재시작, 잘못 복사된 링크를 확인합니다. 문서를 다시 생성해야 할 수 있습니다.
- 인증 요청 만료: AI의 연결 설정에서 새 인증을 시작합니다. 이전 인증 화면을 계속 새로고침하지 않습니다.
- 실제 한글 줄바꿈/표 넘침: 입력을 줄이거나 문서를 검토·수정합니다. 구조 검증 통과는 한글 실조판 보증과 다릅니다.
