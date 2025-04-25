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
