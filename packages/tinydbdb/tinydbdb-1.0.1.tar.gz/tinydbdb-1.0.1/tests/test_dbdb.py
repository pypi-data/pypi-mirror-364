import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from dbdb.dbdb_project import DBDB
import pytest
from datetime import datetime
import time
import subprocess


class Unpicklable:
    def __init__(self):
        self.fp = open(__file__, "r")  

def test_unpicklable_value(tmp_path):
    dbfile = tmp_path / "bad_value.db"
    db = DBDB(str(dbfile))
    oops = Unpicklable()
    with pytest.raises(Exception):
        db.put("bad", oops)

def test_put_get_delete(tmp_path):
    dbfile = tmp_path / "testdb.dat"
    db = DBDB(str(dbfile))
    
    db.put("foo", "bar")
    assert db.get("foo") == "bar"
    
    db.delete("foo")
    assert db.get("foo") is None
    assert db.size() == 0

def test_list_keys_and_exist(tmp_path):
    dbfile = tmp_path / "testdb2.dat"
    db = DBDB(str(dbfile))
    db.put("a", "1")
    db.put("b", "2")
    keys = db.list_keys()
    assert set(keys) == {"a", "b"}
    assert db.exist("a") is True
    assert db.exist("z") is False

def test_clear_and_backup_export(tmp_path):
    dbfile = tmp_path / "testdb3.dat"
    db = DBDB(str(dbfile))
    db.put("x", "y")
    db.clear()
    assert db.size() == 0

    backupfile = tmp_path / "backupfile.dat"
    jsonfile = tmp_path / "db.json"
    db.put("newkey", "newval")
    db.backup(str(backupfile))
    db.export_json(str(jsonfile))
    assert os.path.exists(backupfile)
    assert os.path.exists(jsonfile)

def test_persistence_between_sessions(tmp_path):
    dbfile = tmp_path / "persist_test.db"
    db1 = DBDB(str(dbfile))
    db1.put("session_key", "session_value")
    del db1 

    db2 = DBDB(str(dbfile))  
    assert db2.get("session_key") == "session_value"


def test_large_input(tmp_path):
    dbfile = tmp_path / "large_input.db"
    db = DBDB(str(dbfile))
    big_string = "x" * (10**6)  
    db.put("big", big_string)
    assert db.get("big") == big_string

    big_list = list(range(100000))  
    db.put("list", big_list)
    assert db.get("list") == big_list



def test_metadata_timestamps(tmp_path):
    dbfile = tmp_path / "meta_test.db"
    db = DBDB(str(dbfile))

    created_at = db.data['meta']['created_at']
    updated_at_1 = db.data['meta']['updated_at']
    
    time.sleep(0.5)
    db.put("new", "value")
    updated_at_2 = db.data['meta']['updated_at']

    assert created_at == db.data['meta']['created_at'] 
    assert updated_at_1 != updated_at_2 


def test_cli_put_get(tmp_path):
    script = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'dbdb', 'dbdb_project.py'))
    dbfile = tmp_path / "cli_test.db"

    result = subprocess.run(
        ["python", script, "put", "city", "mumbai", "--db", str(dbfile)],
        capture_output=True, text=True
    )
    assert "Success" in result.stdout

    result = subprocess.run(
        ["python", script, "get", "city", "--db", str(dbfile)],
        capture_output=True, text=True
    )
    assert "mumbai" in result.stdout

def test_cli_list_and_size(tmp_path):
    script = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'dbdb', 'dbdb_project.py'))
    dbfile = tmp_path / "cli_list.db"

    subprocess.run(["python", script, "put", "fruit", "mango", "--db", str(dbfile)])
    subprocess.run(["python", script, "put", "veg", "carrot", "--db", str(dbfile)])

    list_out = subprocess.run(["python", script, "list", "--db", str(dbfile)],
                              capture_output=True, text=True)
    assert "fruit" in list_out.stdout

    size_out = subprocess.run(["python", script, "size", "--db", str(dbfile)],
                              capture_output=True, text=True)
    assert "2" in size_out.stdout


def test_get_meta_fields(tmp_path):
    dbfile = tmp_path / "meta_fields.db"
    db = DBDB(str(dbfile))
    
    created = db.get_created_time()
    updated = db.get_updated_time()
    
    assert isinstance(created, str)
    assert isinstance(updated, str)
    assert created == db.data["meta"]["created_at"]
    assert updated == db.data["meta"]["updated_at"]

def test_metadata_accessors(tmp_path):
    dbfile = tmp_path / "meta_info.db"
    db = DBDB(str(dbfile))
    
    created = db.get_created_time()
    updated = db.get_updated_time()

    assert isinstance(created, str)
    assert isinstance(updated, str)
    assert created == db.data["meta"]["created_at"]
    assert updated == db.data["meta"]["updated_at"]

