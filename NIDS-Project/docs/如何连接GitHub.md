# 连接GitHub仓库完整指南
# 仓库地址：https://github.com/mayname553/NIDS-Project/

## 方法一：SSH连接（推荐，最稳定）

### 步骤1：添加SSH密钥到GitHub（必须先做）

你的SSH公钥：
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDJ7e/xzLHnjPyCL+8yVeAqgsbMX5HVGQ9wgsbyeX0EnaUExP8q7kwx4eoV9Ygq1akvqcoZz/TpyT5lnmp7HzNzQhJD1u2ZiVmujUEyl50Ot2nftPWmsyMUR+ijBwKpaG1dLuji+D+8aVFmm2EagYm6XatpmSGvOFyJbJgdfgw+tbeBIyHsAp72Dbz86RCRfn2Om3wG9YJtSPWr2HAzT02EHASwzrAmNqKtCEdSNPFXvjZktpXTo3sqmCy6nQsxbvnkAdSggKxMdb3izXmaImKBcan65JppIkj8wriCutRF7jDsGULrz7ikUuLcGrW8hYChlnfBysZGpT7wZOnUAYccFKXujY69EdG7Mt3yKmc2m7y8Iph2pNE81iFQHi1KRc/wUTviDEaRsP/GqcoFz0RTkI6+5cRaVedglYxjcqwthgNAMHd6rfmXyYw85xJa+KdyudzJWdekpOPqHxdafkEy+0rZkFtEPtswAMPGIg986zzgKYV1JtArDM2w2dGkaR0= 2370593750@qq.com
```

**操作步骤：**
1. 复制上面的公钥（完整复制，从ssh-rsa到@qq.com）
2. 打开浏览器，访问：https://github.com/settings/keys
3. 点击右上角绿色按钮 "New SSH key"
4. 填写表单：
   - Title: 输入 "我的电脑" 或任意名称
   - Key: 粘贴上面复制的公钥
5. 点击 "Add SSH key"
6. 可能需要输入GitHub密码确认

### 步骤2：修改本地仓库为SSH连接

在你的项目目录（D:\大学\大创\执行文件\NIDS-Project）打开命令行，执行：

```bash
# 修改远程仓库URL为SSH
git remote set-url github git@github.com:mayname553/NIDS-Project.git

# 验证修改
git remote -v
```

应该看到：
```
github  git@github.com:mayname553/NIDS-Project.git (fetch)
github  git@github.com:mayname553/NIDS-Project.git (push)
```

### 步骤3：测试SSH连接

```bash
ssh -T git@github.com
```

**第一次连接会提示：**
```
The authenticity of host 'github.com (...)' can't be established.
Are you sure you want to continue connecting (yes/no)?
```
输入 `yes` 并回车。

**成功的话会看到：**
```
Hi mayname553! You've successfully authenticated, but GitHub does not provide shell access.
```

### 步骤4：推送代码到GitHub

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

---

## 方法二：使用代理（如果你有代理软件）

如果你有Clash、V2Ray等代理软件：

### 步骤1：查看代理端口
打开你的代理软件，查看HTTP代理端口（通常是7890或10809）

### 步骤2：配置Git代理
```bash
# 配置代理（替换7890为你的实际端口）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 验证配置
git config --global --get http.proxy
```

### 步骤3：测试连接
```bash
git ls-remote https://github.com/mayname553/NIDS-Project.git
```

### 步骤4：推送代码
```bash
git add .
git commit -m "docs: 添加项目分析报告和实施指南"
git push github master
```

### 不需要代理时取消配置：
```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

---

## 方法三：临时推送到Gitee（备用方案）

如果上面两个方法都不行，可以先推送到Gitee：

```bash
# 推送到Gitee
git push origin master

# 然后在Gitee网页上使用"同步到GitHub"功能
```

---

## 常见问题解决

### Q1: SSH连接提示 "Permission denied (publickey)"
**原因：** SSH密钥还没添加到GitHub
**解决：** 重新检查步骤1，确保公钥正确添加

### Q2: 推送时提示 "rejected"
**原因：** 远程仓库有新的提交
**解决：**
```bash
git pull github master --rebase
git push github master
```

### Q3: 提示 "fatal: refusing to merge unrelated histories"
**解决：**
```bash
git pull github master --allow-unrelated-histories
git push github master
```

---

## 推荐方案

**最推荐：方法一（SSH连接）**
- 优点：稳定、安全、不需要代理
- 缺点：需要先添加SSH密钥（只需要做一次）

**次推荐：方法二（代理）**
- 优点：配置简单
- 缺点：需要代理软件

---

## 下一步

1. 选择一个方法（推荐方法一）
2. 按步骤操作
3. 如果遇到问题，告诉我具体的错误信息
4. 我会帮你解决

**现在请告诉我：**
- 你想用哪个方法？
- 或者你遇到了什么问题？
