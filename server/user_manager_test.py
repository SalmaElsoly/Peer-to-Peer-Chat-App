import user_manager as UM
import pytest

def test_create_account():
    assert UM.createAccount("acc_test3","Pass123$Test") == "join-success"
def test_create_account2():
    assert UM.createAccount("acc_test3","Pass123$Test") == "join-exists"

def test_Login_User():
    assert UM.loginUser("acc_test3","Pass123$",2,3)=="login-wrong-credentials"
def test_Login_User2():
    assert UM.loginUser("acc_te","Pass123$Test",2,3)=="login-account-not-exist"
def test_Login_User3():
    assert UM.loginUser("acc_test3","Pass123$Test",2,3)=="login-success"
def test_Login_User4():
    assert UM.loginUser("acc_test3","Pass123$Test",2,3)=="login-online"

def test_online_users():
    assert UM.getOnlineUsers("acc_test3")==[]


