from github import Github

def get_github_repo(access_token, repo_name):
    """
    Github Repo Object를 얻는 함수

    매개변수:
    access_token: 깃허브 Access Token
    repo_name: 깃허브 레포지토리 이름
    
    반환 값:
    repo: 레포지토리 객체
    """
    return Github(access_token).get_user().get_repo(repo_name)

def upload_github_issue(repo, title, body):
    """
    Github에 Issue를 올리는 함수
    
    매개변수:
    repo: 깃허브 레포지토리 객체
    title: Issue 제목
    body: Issue 내용
    """
    repo.create_issue(title=title, body=body)