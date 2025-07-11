## 1.0.1

### Various fixes & improvements

- Update phrasing as we might report non write actions (#102) by @kneeyo1
- add approval policy and storage abstract classes (#101) by @lynnagara
- Adding tests for flask endpoints. starting with health (#83) by @kneeyo1

## 1.0.0

### Various fixes & improvements

- implement new design (#100) by @lynnagara
- split up the script result component (#99) by @lynnagara

## 0.2.9

### Various fixes & improvements

- fix autocomplete z-index (for real this time) (#98) by @lynnagara
- move the get_config function (#96) by @lynnagara
- dynamic page title (#97) by @lynnagara
- Add re execution to the scripts  (#95) by @kneeyo1
- autocomplete: ui improvements (#93) by @lynnagara
- fix: Fix circular dependency (#94) by @lynnagara

## 0.2.8

### Various fixes & improvements

- fix autocomplete (#92) by @lynnagara

## 0.2.7

### Various fixes & improvements

- test utilities for autocomplete (#90) by @lynnagara
- fix empty headers in /autocomplete endpoint (#91) by @lynnagara

## 0.2.6

### Various fixes & improvements

- feat: dynamic autocomplete (#88) by @lynnagara
- add extra package (#89) by @kneeyo1
- Refactoring to blueprints (#87) by @kneeyo1
- autocomplete part 2: frontend component (#86) by @lynnagara
- autocomplete: adding the backend type and api endpoint (#85) by @lynnagara
- add Slack Event notifier (#81) by @kneeyo1
- docs: fix devserver command (#82) by @lynnagara

## 0.2.5

### Various fixes & improvements

- Add some error handling for a failed region (#77) by @kneeyo1
- Fix typing issues with mypy (#80) by @kneeyo1
- custom function parameters and input types (#78) by @lynnagara
- if user has no groups display list of groups they don't have access to (#79) by @lynnagara
- remove build-docker-image job (#73) by @lynnagara

## 0.2.4

### Various fixes & improvements

- remove weird scrolling of nav headings (#76) by @lynnagara
- fix scrolling on docs pages (#75) by @lynnagara

## 0.2.3

### Various fixes & improvements

- render documentation in the UI (#74) by @lynnagara
- fix style for long text in nav (#72) by @lynnagara

## 0.2.2

### Various fixes & improvements

- improve testing utilities (#71) by @lynnagara
- remove a bunch of stuff that moved into sentry-scripts (#70) by @lynnagara
- improve chart (#69) by @lynnagara
- revert api changes (#68) by @lynnagara
- validation: check all functions have string args on startup (#67) by @lynnagara

## 0.2.1

### Various fixes & improvements

- add confirmation step for write actions (#66) by @lynnagara
- Style Cleanup (#65) by @jmanhart

## 0.2.0

### Various fixes & improvements

- Adding in a status tag to highlight read/write functionality  (#63) by @jmanhart

## 0.1.9

### Various fixes & improvements

- fix kafka module: confluent kafka requires this to be a dict (#62) by @lynnagara
- more fixes for checking google group membership (#61) by @lynnagara
- pass the right args to get_group_membership (#60) by @lynnagara

## 0.1.8

### Various fixes & improvements

- add testing utility (#59) by @lynnagara
- google iap: check transitive membership (#58) by @lynnagara
- minor ui tweaks (#56) by @lynnagara
- fix typing (#57) by @kneeyo1
- add github as release target (#55) by @lynnagara
- release: 0.1.7 (c48c02e0) by @getsentry-bot
- rename scripts -> bin (#54) by @lynnagara
- add more documentation to the groups (#53) by @lynnagara
- ops script runner is probably not a good name anymore (#52) by @lynnagara
- fix bad merge which broke the app (#51) by @lynnagara
- fix formatting for pre commit (#50) by @kneeyo1
- add sentry-kube example (#46) by @lynnagara
- fix codeowners (#49) by @lynnagara
- release: 0.1.6 (c2aa5680) by @getsentry-bot
- fix broken build (#48) by @lynnagara
- use flask blueprint (#45) by @lynnagara
- adjust the files in the package (#47) by @lynnagara
- a better function api (#43) by @lynnagara
- export py.typed markers (#44) by @lynnagara
- release: 0.1.5 (f11ea206) by @getsentry-bot
- google-api-client: use a version already in the internal pypi (#42) by @lynnagara
- release: 0.1.4 (1ad3772a) by @getsentry-bot
- fixing group membership (#41) by @lynnagara
- fix reference to directory v1 (#40) by @lynnagara

_Plus 17 more_

## 0.1.7

### Various fixes & improvements

- rename scripts -> bin (#54) by @lynnagara
- add more documentation to the groups (#53) by @lynnagara
- ops script runner is probably not a good name anymore (#52) by @lynnagara
- fix bad merge which broke the app (#51) by @lynnagara
- fix formatting for pre commit (#50) by @kneeyo1
- add sentry-kube example (#46) by @lynnagara
- fix codeowners (#49) by @lynnagara
- release: 0.1.6 (c2aa5680) by @getsentry-bot
- fix broken build (#48) by @lynnagara
- use flask blueprint (#45) by @lynnagara
- adjust the files in the package (#47) by @lynnagara
- a better function api (#43) by @lynnagara
- export py.typed markers (#44) by @lynnagara
- release: 0.1.5 (f11ea206) by @getsentry-bot
- google-api-client: use a version already in the internal pypi (#42) by @lynnagara
- release: 0.1.4 (1ad3772a) by @getsentry-bot
- fixing group membership (#41) by @lynnagara
- fix reference to directory v1 (#40) by @lynnagara
- naive implementation of checking if user is in google group (#39) by @lynnagara
- Revert "dockerfile: swap gunicorn for pyuwsgi (#36)" (#38) by @lynnagara
- add codeowners (#37) by @lynnagara
- dockerfile: swap gunicorn for pyuwsgi (#36) by @lynnagara
- add pre commit stuff (#32) by @kneeyo1
- fix assertion in google iap (#35) by @lynnagara

_Plus 11 more_

## 0.1.6

### Various fixes & improvements

- fix broken build (#48) by @lynnagara
- use flask blueprint (#45) by @lynnagara
- adjust the files in the package (#47) by @lynnagara
- a better function api (#43) by @lynnagara
- export py.typed markers (#44) by @lynnagara
- release: 0.1.5 (f11ea206) by @getsentry-bot
- google-api-client: use a version already in the internal pypi (#42) by @lynnagara
- release: 0.1.4 (1ad3772a) by @getsentry-bot
- fixing group membership (#41) by @lynnagara
- fix reference to directory v1 (#40) by @lynnagara
- naive implementation of checking if user is in google group (#39) by @lynnagara
- Revert "dockerfile: swap gunicorn for pyuwsgi (#36)" (#38) by @lynnagara
- add codeowners (#37) by @lynnagara
- dockerfile: swap gunicorn for pyuwsgi (#36) by @lynnagara
- add pre commit stuff (#32) by @kneeyo1
- fix assertion in google iap (#35) by @lynnagara
- iap: include pyopenssl + allow 30 seconds clock skew (#34) by @lynnagara
- include exc info in sentry logs (#33) by @lynnagara
- remove gunicorn from application requirements (#31) by @lynnagara
- debugging google auth (#30) by @lynnagara
- bump down to support 3.11.8 (#29) by @kneeyo1
- release: 0.1.0 (#22) by @kneeyo1
- Add frontend files to the manifest  (#27) by @kneeyo1
- one more spot that needs rename (#28) by @lynnagara

_Plus 3 more_

## 0.1.5

### Various fixes & improvements

- google-api-client: use a version already in the internal pypi (#42) by @lynnagara
- release: 0.1.4 (1ad3772a) by @getsentry-bot
- fixing group membership (#41) by @lynnagara
- fix reference to directory v1 (#40) by @lynnagara
- naive implementation of checking if user is in google group (#39) by @lynnagara
- Revert "dockerfile: swap gunicorn for pyuwsgi (#36)" (#38) by @lynnagara
- add codeowners (#37) by @lynnagara
- dockerfile: swap gunicorn for pyuwsgi (#36) by @lynnagara
- add pre commit stuff (#32) by @kneeyo1
- fix assertion in google iap (#35) by @lynnagara
- iap: include pyopenssl + allow 30 seconds clock skew (#34) by @lynnagara
- include exc info in sentry logs (#33) by @lynnagara
- remove gunicorn from application requirements (#31) by @lynnagara
- debugging google auth (#30) by @lynnagara
- bump down to support 3.11.8 (#29) by @kneeyo1
- release: 0.1.0 (#22) by @kneeyo1
- Add frontend files to the manifest  (#27) by @kneeyo1
- one more spot that needs rename (#28) by @lynnagara
- build: remove hardcoded python version (#25) by @lynnagara
- typo fix since we renamed dir (#24) by @kneeyo1
- add Workflows for release publishing (#23) by @kneeyo1

## 0.1.4

### Various fixes & improvements

- fixing group membership (#41) by @lynnagara
- fix reference to directory v1 (#40) by @lynnagara
- naive implementation of checking if user is in google group (#39) by @lynnagara
- Revert "dockerfile: swap gunicorn for pyuwsgi (#36)" (#38) by @lynnagara
- add codeowners (#37) by @lynnagara
- dockerfile: swap gunicorn for pyuwsgi (#36) by @lynnagara
- add pre commit stuff (#32) by @kneeyo1
- fix assertion in google iap (#35) by @lynnagara
- iap: include pyopenssl + allow 30 seconds clock skew (#34) by @lynnagara
- include exc info in sentry logs (#33) by @lynnagara
- remove gunicorn from application requirements (#31) by @lynnagara
- debugging google auth (#30) by @lynnagara
- bump down to support 3.11.8 (#29) by @kneeyo1
- release: 0.1.0 (#22) by @kneeyo1
- Add frontend files to the manifest  (#27) by @kneeyo1
- one more spot that needs rename (#28) by @lynnagara
- build: remove hardcoded python version (#25) by @lynnagara
- typo fix since we renamed dir (#24) by @kneeyo1
- add Workflows for release publishing (#23) by @kneeyo1

## 0.1.0

- Inital release.
