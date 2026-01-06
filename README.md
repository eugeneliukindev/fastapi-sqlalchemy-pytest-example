```shell
cd app
docker compose -p=test --env-file=.env.test up --build --exit-code-from fastapi --abort-on-container-exit
```