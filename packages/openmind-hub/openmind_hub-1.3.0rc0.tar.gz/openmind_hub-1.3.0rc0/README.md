# openMind Hub Client

## 简介

openMind Hub Client可以帮助您在不离开开发环境的情况下与社区进行交互。您可以轻松创建和管理仓库，下载和上传文件以及从模型库获取有用的模型和数据集元数据。

## 安装

关于openMind Hub Client的安装步骤，推荐用户参考[《安装》](https://modelers.cn/docs/zh/openmind-hub-client/install.html)文档，以确保顺利并正确地完成安装过程。

## 下载文件

例如，下载[t5_small](https://modelers.cn/models/PyTorch-NPU/t5_small/)模型配置文件：

```py
from openmind_hub import om_hub_download

om_hub_download(repo_id="PyTorch-NPU/t5_small", filename="config.json")
```

详见[《下载指南》](https://modelers.cn/docs/zh/openmind-hub-client/basic_tutorial/download.html)。

## 访问令牌

访问私有仓库资源、创建仓库和上传文件等场景都需要使用访问令牌（即token）才能与社区进行交互。请[创建访问令牌](https://modelers.cn/my/tokens)并妥善保存，令牌内容仅会在创建时显示。

## 上传文件

使用`upload_folder`为您的仓库上传文件，示例如下：

```py
from openmind_hub import upload_folder
upload_folder(
    repo_id="owner/repo",
    folder_path="./folder_to_upload",
    token="xxx",
)
```

+ `token`：对目标仓库具有可写权限的访问令牌，必选。
+ `repo_id`：文件要上传到的仓库，必选。
+ `folder_path`：要上传目录的绝对路径或相对路径，上传的内容不包含该目录本身，必选。支持字符串或Path类型，如：`"./folder"`或`Path("./folder")`。

详见[《上传文件》](https://modelers.cn/docs/zh/openmind-hub-client/basic_tutorial/upload.html)。

## 贡献

1. 在提交PR之前，请确保所有测试都通过。首先在本地运行如下命令。

    ```shell
    # The scripts below run on system default python version by default. If you want to use other python version, set the env
    # PY_VERSION. For example, `PY_VERSION=3.10 ./ci/lint.sh`
    # Lint check
    ./ci/lint.sh
    # Unit test
    ./ci/unit_test.sh
    # Functional test, Please generate the HUB_TOKEN by yourself and use it privatelly.
    HUB_TOKEN=your_hub_token ./ci/functional_test.sh
    ```

2. 当您推送或更新PR（Pull Request）后，系统将自动触发CI（持续集成）构建和测试流程。若所有CI构建和测试均顺利通过，`ci-success`标记将自动添加到您的PR中。然而，若出现CI故障，您可以点击CI日志链接以详细查看失败原因，并在本地进行必要的修复。一旦您完成了修复并希望重新运行CI作业，只需在PR中留下评论`/recheck`即可。

## 安全声明

为保障使用过程安全，推荐用户参考[《安全声明》](./security_statement.md)了解相关安全信息，进行必要的安全加固。