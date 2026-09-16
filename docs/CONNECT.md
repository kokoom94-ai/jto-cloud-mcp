# ChatGPT · Claude · Gemini 연결

확인 기준일: 2026-09-16. 앱의 메뉴·계정 조건은 바뀔 수 있습니다. 아래는 연결 준비 안내이며 실제 세 앱 시험 완료 선언이 아닙니다.

## 공통

운영자가 배포한 HTTPS 서버의 `/mcp` 주소가 필요합니다. GitHub 저장소 주소를 MCP 서버 URL 칸에 넣지 마세요. 최초 OAuth 승인 화면에 운영자의 연결 암호를 입력합니다. 암호는 AI 대화에 보내지 마세요.

서버는 Streamable HTTP·OAuth 검색·동적 클라이언트 등록·PKCE를 지원합니다. 파일은 HTTPS 링크와 MCP `resource_link`를 함께 반환합니다. 앱마다 링크/첨부 카드 표시가 달라 동일한 모양은 보장하지 않습니다.

## ChatGPT

맞춤 앱/커넥터 개발 연결을 사용할 수 있는 계정에서 원격 MCP URL을 등록합니다. 관리자 설정 또는 개발 연결 기능 활성화가 필요할 수 있습니다. 등록 뒤 OAuth 승인을 마치고 JTO 도구를 선택해 요청합니다.

공개 앱 디렉터리 등록은 별도 심사 절차입니다. 이 저장소를 공개해도 디렉터리에 자동 등록되지는 않습니다.

[OpenAI MCP 서버 문서](https://developers.openai.com/plugins/build/mcp-server) · [연결·시험](https://developers.openai.com/plugins/deploy/connect-chatgpt)

## Claude

설정의 커넥터에서 맞춤 커넥터를 추가하고 서버 URL을 입력합니다. 조직 설정에 따라 관리자가 등록해야 할 수 있습니다. Claude는 원격 서버를 클라우드에서 호출하므로 사용자 PC를 켜둘 필요가 없습니다.

[Anthropic 공식 연결 안내](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)

## Gemini

공식 도움말에서 확인한 현재 맞춤 앱 연결 조건은 **미국, 18세 이상, 개인 Google 계정, Keep Activity 켜짐, 영어 지원**입니다. 한국 사용자/조직 계정에서 바로 사용할 수 있다고 보장하지 않습니다.

사용 가능한 계정에서는 Gemini 웹의 Settings → Connected Apps → Custom apps에서 MCP URL을 등록하고 승인을 완료합니다. 웹에서 연결하면 지원되는 모바일 앱에서도 사용할 수 있다고 안내되어 있습니다.

Gemini API/CLI의 MCP 사용과 일반 Gemini 앱 연결은 별도입니다. API/CLI 테스트를 일반 대화창 호환 시험으로 대신하지 않습니다. 지원 지역을 우회하는 방법은 이 배포 절차에 포함하지 않습니다.

[Google 공식 맞춤 앱 연결 안내](https://support.google.com/gemini/answer/17209137?co=GENIE.Platform%3DDesktop&hl=en-TZ)

## 동료에게 공유할 내용

“이 서비스는 JTO 사업계획·결과보고·1PAGE 양식으로 문서를 생성합니다. 아래 MCP 주소를 AI의 맞춤 커넥터 설정에 등록하고 연결을 승인하세요. 연결 후 ‘2027 중화권 마케팅 사업계획을 작성해줘’ 또는 ‘이 내용을 1PAGE로 만들어줘’라고 요청하면 대화에서 다운로드 링크를 받을 수 있습니다.”

위 안내에 실제 배포 후 확인한 MCP 주소를 추가하세요. GitHub 주소는 소스·설치 안내용으로 함께 공유할 수 있습니다.
