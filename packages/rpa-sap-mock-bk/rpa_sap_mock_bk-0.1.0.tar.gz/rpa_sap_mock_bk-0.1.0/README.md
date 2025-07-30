hư viện Robot Framework để tích hợp SAP Cloud SDK.

## Cài đặt

```bash
pip install rpa-sap
```

## Sử dụng trong Robot

```robot
*** Settings ***
Library    rpa_sap

*** Variables ***
${BASE_URL}      https://your-sap-url.com
${TOKEN}         your-access-token

*** Test Cases ***
Test SAP API
    Connect To SAP System    ${BASE_URL}    ${TOKEN}
    ${json}=    Set Variable    {"houseNumber": "123"}
    ${result}=    Update Business Partner Address    1003764    28238    ${json}
    Log    ${result}
```

## License

MIT
