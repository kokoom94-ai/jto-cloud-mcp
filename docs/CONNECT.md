# 직원용 AI 연결 안내 — 로그인·암호 없음

확인 기준일: 2026-09-17. 원격 공개 MCP이며 직원 PC에 서버를 설치하지 않습니다.

**연결 주소: https://jto-cloud-mcp.onrender.com/mcp**

이름은 JTO 문서 도구, 인증은 **없음 / No authentication / None**으로 선택합니다. 연결 암호, OAuth Client ID, Client Secret은 입력하지 않습니다. 예전에 OAuth로 등록했다면 기존 JTO 연결을 제거하고 인증 없음으로 다시 등록합니다.

## ChatGPT

1. 플러그인/앱 관리 화면의 추가(+)를 선택합니다. 계정에 따라 설정 → 앱 → 만들기 또는 개발 연결 메뉴가 표시될 수 있습니다.
2. 이름 JTO 문서 도구, 설명 제주관광공사 사업계획·결과보고·1PAGE 양식 문서 생성을 입력합니다.
3. 위 서버 URL을 입력하고 인증을 **없음**으로 설정합니다.
4. 도구 검색/등록을 완료합니다. jto_template_info, jto_generate_document가 표시되는지 확인합니다.
5. 새 대화의 도구 메뉴에서 JTO를 선택하고 아래 확인 문장을 요청합니다.

조직 계정은 관리자의 맞춤 앱/개발 연결 권한이 필요할 수 있습니다. GitHub 공개는 앱 디렉터리 등재와 별개이며, 대화에 URL만 붙이는 것으로 등록되지는 않습니다.
[OpenAI 공식 연결 안내](https://developers.openai.com/plugins/deploy/connect-chatgpt)

## Claude

1. Customize → Connectors → + → Add custom connector를 엽니다.
2. 이름 JTO 문서 도구, 서버 URL에 위 연결 주소를 입력합니다.
3. 고급 OAuth Client ID/Secret은 비워 둡니다. 인증 선택이 있으면 **없음**을 선택하고 Add/Connect를 완료합니다.
4. 대화 입력창 + → Connectors에서 JTO를 켭니다.
5. 아래 확인 문장을 요청하고 생성된 링크를 눌러 파일을 받습니다.

Team/Enterprise는 관리자가 Organization settings → Connectors에서 먼저 등록해야 할 수 있습니다. 호출은 Anthropic의 클라우드에서 이루어집니다.
[Claude 공식 연결 안내](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)

## Gemini

Google 맞춤 앱 도움말의 조건은 **미국, 18세 이상, 개인 Google 계정, Keep Activity 켜짐, 영어 지원**입니다. Spark 전체 제공 지역 확대와 맞춤 앱의 제공 조건은 다를 수 있습니다. 한국 계정에서 바로 연결된다고 보장하지 않습니다.

1. 지원되는 계정으로 Gemini 웹에 로그인합니다.
2. Settings → Connected Apps를 엽니다. 보이지 않으면 Personal Intelligence → Connected Apps를 확인합니다.
3. Custom apps → Add a custom app에 위 연결 주소를 입력합니다.
4. Next를 눌러 등록합니다. 이 서버는 인증이 없으므로 자격증명을 입력하지 않습니다. 해당 계정에서 인증 없는 MCP 등록을 거부하면 그 오류를 확인해야 하며 연결 성공으로 간주하지 않습니다.
5. 대화에서 @로 JTO 앱을 선택하고 아래 확인 문장을 요청합니다.

Gemini API/CLI 시험은 일반 Gemini 대화창 시험과 다릅니다. 실제 계정의 메뉴·연결·파일 다운로드 확인이 필요합니다.
[Google 공식 맞춤 앱 안내](https://support.google.com/gemini/answer/17209137?co=GENIE.Platform%3DDesktop&hl=en-TZ)

## 최초 확인 및 요청 예시

- 연결 확인: JTO 도구의 jto_template_info를 실제 호출해서 사업계획·결과보고·1PAGE 세 양식이 있는지 확인해줘.
- 사업계획: 2027 중화권 마케팅 사업계획을 JTO 사업계획 양식으로 작성하고 HWPX 다운로드 링크를 줘. 미확정 예산은 산정 가정과 확정 여부를 구분하고, 음슴체 내부 품의 문체로 작성해줘.
- 결과보고: 첨부한 실제 실적으로 JTO 결과보고 HWPX를 만들어줘. 없는 실적이나 집행액은 만들어내지 마.
- 1PAGE: 이 내용을 JTO 1PAGE 양식으로 요약하고 HWP 다운로드 링크를 줘.

AI는 내용을 작성하고 JTO 서버가 양식 파일을 생성합니다. 결과의 실제 다운로드 링크로 받습니다. 파일 카드 모양은 앱마다 다를 수 있습니다. AI가 말로 성공했다고 답한 것만으로는 연결 확인이 아닙니다.

## 알아둘 사항

- 로그인은 없지만 HTTPS와 파일별 서명·만료는 유지됩니다.
- 생성 문서 목록은 공개하지 않습니다. 링크를 가진 사람은 만료 전 파일을 받을 수 있습니다. 문서별 재조회 키는 도구가 자동 반환하며 직원이 암호로 입력하는 값이 아닙니다.
- 무료 서버의 첫 호출은 늦을 수 있습니다. 안내 페이지가 열린 뒤 다시 연결합니다.
- 기본 링크 유효기간은 24시간입니다. 무료 서버 재시작 시 그 전에 파일이 사라질 수 있어 생성 후 내려받습니다.
- 다운로드 404는 만료·재시작·잘못 복사한 링크를 확인하고 문서를 다시 생성합니다.
- Authentication required가 나오면 이전 OAuth 연결 또는 구버전 배포를 확인합니다.
- 구조 검증은 한글 실제 줄바꿈·표 넘침 검증과 다릅니다. 최종 제출 전 한글에서 검토합니다.

안내 페이지: https://jto-cloud-mcp.onrender.com/
공개 소스: https://github.com/kokoom94-ai/jto-cloud-mcp
