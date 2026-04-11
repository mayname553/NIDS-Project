# 快速连接GitHub - SSH配置步骤

## 第一步：复制你的SSH公钥

你的SSH公钥内容如下（请完整复制）：

```
[公钥内容将在下面显示]
```

## 第二步：添加SSH密钥到GitHub

1. 访问：https://github.com/settings/keys
2. 点击右上角绿色按钮 "New SSH key"
3. 填写信息：
   - Title: 随便起个名字，比如 "我的电脑"
   - Key: 粘贴上面的公钥内容（完整复制，从ssh-rsa开头到邮箱结尾）
4. 点击 "Add SSH key"
5. 可能需要输入GitHub密码确认

## 第三步：修改本地仓库为SSH连接

在你的项目目录执行以下命令：

```bash
# 修改GitHub远程仓库URL为SSH
git remote set-url github git@github.com:mayname553/NIDS-Project.git

# 验证修改
git remote -v
```

## 第四步：测试SSH连接

```bash
# 测试SSH连接
ssh -T git@github.com

# 如果看到类似这样的消息说明成功：
# Hi mayname553! You've successfully authenticated, but GitHub does not provide shell access.
```

## 第五步：推送代码到GitHub

```bash
# 查看当前状态
git status

# 添加所有更改
git add .

# 提交
git commit -m "docs: 添加项目分析报告和实施指南"

# 推送到GitHub
git push github master
```

## 如果遇到问题

### 问题1：ssh -T git@github.com 提示 "Permission denied"
解决：说明SSH密钥还没添加到GitHub，请重新检查第二步

### 问题2：第一次连接提示 "authenticity of host"
解决：输入 yes 并回车，这是正常的

### 问题3：推送时提示 "rejected"
解决：先执行 git pull github master --rebase，然后再推送

---

**下一步：请先完成第二步（添加SSH密钥到GitHub），然后告诉我，我会帮你执行后续步骤。**
