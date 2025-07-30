# 혁랭 (Hyuk-Lang)

한글 기반 난해한 포인터 언어.  
아래 6개의 명령어만으로 동작합니다:

## 명령어 문법

| 명령어 | 의미 |
|--------|------|
| `.`    | 현재 포인터의 값을 +1 |
| `,`    | 현재 포인터의 값을 -1 |
| `김`   | 현재 값을 유니코드 문자로 출력 |
| `미`   | 포인터를 왼쪽으로 이동 |
| `민`   | 포인터를 오른쪽으로 이동 |
| `혁`   | 실행 종료 |

## 메모리 및 값 제한

- 메모리: 30000개의 셀
- 포인터 위치: 0~29999
- 각 셀의 값 범위: 0 ~ 1114111 (유니코드 `chr()` 함수 출력 범위)

값이 이 범위를 벗어나면 실행 중 오류가 발생합니다.

## 필요 Python 버전

Python 3.8 이상

## 설치

```bash
pip install hyuk-lang
```

## 사용법

### CLI

```bash
hyuk 파일명.hyuk
```

### GUI

```bash
hyuk-editor
```

## 사용 예시

```bash
hyuk examples/A.hyuk
```

출력:

```
A
```

## 예제 파일

`examples/` 폴더를 참고하세요.

## 라이선스

MIT License  
자세한 내용은 [LICENSE](https://github.com/JoonwooM/hyuk-lang/blob/main/LICENSE)를 참고하세요.

## 개발자

[JoonwooM](https://github.com/JoonwooM)