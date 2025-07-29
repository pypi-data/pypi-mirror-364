import pandas as pd
import pytest
from sqlalchemy import create_engine
import ChemInformant as ci  # 可以直接导入，因为 pytest 会处理路径

# --- 测试数据 (在所有测试开始前只获取一次) ---
# 使用 pytest.fixture 来创建只执行一次的共享数据
@pytest.fixture(scope="session")
def test_data():
    """Fixture to fetch all necessary test data from PubChem once per test session."""
    print("\n(Fetching test data from PubChem...)")
    return {
        "aspirin": ci.get_properties(["aspirin"], ["cas", "xlogp"]),
        "others": ci.get_properties(["caffeine", "ibuprofen"], ["cas", "xlogp"]),
        "empty": pd.DataFrame(columns=["input_identifier", "cid", "status", "cas"]),
    }

# --- Fixture: 核心资源 ---
# 这是 pytest 的魔法：一个可重用的“资源准备”函数
@pytest.fixture
def in_memory_engine():
    """
    Creates a new, clean in-memory SQLite engine for each test function.
    The `yield` keyword passes the engine to the test, and the code after
    `yield` is the cleanup, which runs after the test is done.
    """
    engine = create_engine("sqlite:///:memory:")
    yield engine
    engine.dispose() # 清理连接


# --- 测试用例 (Test Cases) ---
# 每个函数都是一个独立的测试，pytest 会自动发现并运行它们

TABLE_NAME = "test_table"

def test_if_exists_replace(in_memory_engine, test_data):
    """
    Tests that if_exists='replace' correctly overwrites existing data.
    """
    # 将引擎和测试数据作为参数传入，pytest 会自动注入它们
    df_aspirin = test_data["aspirin"]
    df_others = test_data["others"]

    # 第一次写入
    ci.df_to_sql(df_aspirin, in_memory_engine, TABLE_NAME, if_exists="replace")
    count1 = pd.read_sql(f"SELECT COUNT(*) FROM {TABLE_NAME}", in_memory_engine).iloc[0, 0]
    assert count1 == 1, "Failed to write initial data"

    # 第二次写入（覆盖）
    ci.df_to_sql(df_others, in_memory_engine, TABLE_NAME, if_exists="replace")
    count2 = pd.read_sql(f"SELECT COUNT(*) FROM {TABLE_NAME}", in_memory_engine).iloc[0, 0]
    assert count2 == 2, "if_exists='replace' failed to overwrite data"


def test_if_exists_append(in_memory_engine, test_data):
    """
    Tests that if_exists='append' correctly adds new data without deleting old data.
    """
    df_aspirin = test_data["aspirin"]
    df_others = test_data["others"]

    # 第一次写入
    ci.df_to_sql(df_aspirin, in_memory_engine, TABLE_NAME, if_exists="replace")
    # 第二次写入（追加）
    ci.df_to_sql(df_others, in_memory_engine, TABLE_NAME, if_exists="append")

    total_count = pd.read_sql(f"SELECT COUNT(*) FROM {TABLE_NAME}", in_memory_engine).iloc[0, 0]
    expected_count = len(df_aspirin) + len(df_others)
    assert total_count == expected_count, "if_exists='append' failed to add new data"


def test_if_exists_fail(in_memory_engine, test_data):
    """
    Tests that if_exists='fail' raises a ValueError when the table already exists.
    """
    df_aspirin = test_data["aspirin"]
    df_others = test_data["others"]
    
    # 先创建表
    ci.df_to_sql(df_aspirin, in_memory_engine, TABLE_NAME)

    # 使用 pytest.raises 来检查是否抛出了预期的异常
    # 这是一个比 try/except 更简洁、更强大的测试异常的方法
    with pytest.raises(ValueError, match="already exists"):
        ci.df_to_sql(df_others, in_memory_engine, TABLE_NAME, if_exists="fail")


def test_writing_empty_dataframe(in_memory_engine, test_data):
    """
    Tests that writing an empty DataFrame creates an empty table without errors.
    """
    df_empty = test_data["empty"]
    ci.df_to_sql(df_empty, in_memory_engine, TABLE_NAME, if_exists="replace")
    
    count = pd.read_sql(f"SELECT COUNT(*) FROM {TABLE_NAME}", in_memory_engine).iloc[0, 0]
    assert count == 0, "Writing an empty DataFrame did not result in an empty table"