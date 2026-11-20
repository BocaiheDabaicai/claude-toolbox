# 后端测试模板

- `conftest.py`：FastAPI + httpx AsyncClient；
- `test_health.py`：健康检查示例。

集成测试建议：

1. 使用独立测试 database（如 `app_test`）；
2. 每个测试用例事务回滚，或每个测试文件重建 schema；
3. 迁移在测试启动前执行一次；
4. 不要连生产/开发库；
5. 认证用测试用户/测试 token；
6. 对写接口清理测试数据。

FastAPI 项目直接参考 `fastapi-service` Skill 的 `assets/template/tests/`。
