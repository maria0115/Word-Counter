import os
import sys
import re
from datetime import datetime, timedelta
from google import genai
from git import Repo

# ==========================================
# [설정 항목] 내 블로그 환경에 맞게 수정해줘!
# ==========================================
BLOG_POSTS_DIR = "./content/blog"  # MDX 파일이 저장될 디렉토리 경로
BLOG_TECH_STACK = "Java 25, Spring Boot 4.0, JPA/Hibernate, Docker, PostgreSQL, Backend Architecture"
PUBLISH_INTERVAL_DAYS = 2  # 포스팅 간격 설정 (2 = 최소 2일 간격으로 발행)
# ==========================================

def get_recent_posts_summary():
    """기존 MDX 파일들을 분석하여 최근 포스팅 날짜와 주제 히스토리를 추출합니다."""
    if not os.path.exists(BLOG_POSTS_DIR):
        return None, []
    
    mdx_files = [f for f in os.listdir(BLOG_POSTS_DIR) if f.endswith('.mdx')]
    if not mdx_files:
        return None, []
        
    history = []
    latest_date = None
    
    # Frontmatter에서 title과 date를 추출하기 위한 정규표현식
    title_re = re.compile(r'^title:\s*["\']?(.*?)["\']?$', re.MULTILINE)
    date_re = re.compile(r'^date:\s*["\']?(.*?)["\']?$', re.MULTILINE)
    
    for file in mdx_files:
        file_path = os.path.join(BLOG_POSTS_DIR, file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
                title_match = title_re.search(content)
                date_match = date_re.search(content)
                
                title = title_match.group(1).strip() if title_match else file
                
                if date_match:
                    date_str = date_match.group(1).strip()[:10]  # YYYY-MM-DD 포맷 가정
                    try:
                        file_date = datetime.strptime(date_str, "%Y-%m-%d")
                        if latest_date is None or file_date > latest_date:
                            latest_date = file_date
                    except ValueError:
                        pass
                
                history.append(f"- {title}")
        except Exception as e:
            print(f"⚠️ {file} 파일 읽기 실패: {e}")
            
    return latest_date, history

def generate_blog_content(history):
    """이전 게시글 히스토리를 기반으로 겹치지 않는 새로운 주제의 MDX를 생성합니다."""
    print("🤖 Gemini가 히스토리를 분석하여 다음 연계 주제를 고민하는 중...")
    
    client = genai.Client()
    
    history_context = "\n".join(history) if history else "기존 포스팅 없음 (첫 글)"
    
    prompt = f"""
    당신은 고급 백엔드 개발자이자 기술 블로그 운영자입니다.
    기존에 작성된 블로그 주제를 확인하고, 내용이 중복되거나 겹치지 않으면서 다음 단계로 깊이 있게 발전할 수 있는 새로운 연계 기술 주제를 하나 선정하여 MDX 형식의 글을 작성해주세요.
    기존 글의 맥락을 이어받아 심화된 개념이나 다른 측면의 해결책을 다루는 것이 좋습니다.
    
    [관심 기술 스택]: {BLOG_TECH_STACK}
    
    [기존 작성된 포스팅 목록]:
    {history_context}
    
    [요구사항]:
    1. 제목은 개발자의 호기심을 유발하고 명확해야 하며, 기존 목록에 있는 주제와 절대 겹치지 않아야 합니다.
    2. MDX Frontmatter(메타데이터)를 상단에 포함해야 합니다. (title, date, tags, description 형식)
       - date는 오늘 날짜인 '{datetime.now().strftime("%Y-%m-%d")}'로 설정해주세요.
    3. 본문은 가상의 데이터나 플레이스홀더를 쓰지 말고, 실제 구동 가능한 수준의 구체적인 코드 예시(Java/Spring 등)를 포함하여 작성해주세요.
    4. 어조는 주니어와 시니어 모두에게 도움되는 '친절하면서도 전문적인 피어(Peer)'의 톤앤매너를 유지하세요.
    
    출력은 다른 설명 없이 오직 MDX 파일 내용만 반환하세요.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text

def save_mdx_file(content):
    """생성된 내용을 mdx 파일로 저장합니다."""
    if not os.path.exists(BLOG_POSTS_DIR):
        os.makedirs(BLOG_POSTS_DIR)
        
    current_date = datetime.now().strftime("%Y-%m-%d")
    # 파일명 중복 및 특수문자 방지를 위한 유니크 파일명 생성
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"{current_date}-{timestamp}-post.mdx"
    file_path = os.path.join(BLOG_POSTS_DIR, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"📝 새 게시글 파일 저장 완료: {file_path}")
    return file_path

def git_push_all():
    """git add ., commit, push 과정을 자동화합니다."""
    print("🚀 Git 자동화 작업 시작...")
    try:
        repo = Repo(os.getcwd())
        repo.git.add(A=True)
        
        current_date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        commit_message = f"Feat: Auto published post - {current_date_str}"
        
        repo.index.commit(commit_message)
        print(f"💾 커밋 완료: '{commit_message}'")
        
        active_branch = repo.active_branch.name
        origin = repo.remote(name='origin')
        print(f"정방향 푸시 중... (branch: {active_branch})")
        origin.push(active_branch)
        
        print("✅ GitHub Push 성공! 블로그 배포가 시작되었습니다.")
    except Exception as e:
        print(f"❌ Git 작업 중 에러 발생: {e}", file=sys.stderr)

if __name__ == "__main__":
    try:
        # 1. 기존 게시글 분석 및 날짜 체크
        latest_date, history = get_recent_posts_summary()
        
        if latest_date:
            days_since_last_post = (datetime.now() - latest_date).days
            print(f"📊 마지막 포스팅 날짜: {latest_date.strftime('%Y-%m-%d')} (현재 {days_since_last_post}일 경과)")
            
            # 발행 간격 조건(예: 2일)을 만족하지 못하면 스크립트 안전 종료
            if days_since_last_post < PUBLISH_INTERVAL_DAYS:
                print(f"⏸️ 설정된 포스팅 간격({PUBLISH_INTERVAL_DAYS}일)이 아직 지나지 않았습니다. 프로그램을 종료합니다.")
                sys.exit(0)
        else:
            print("🆕 기존 포스팅이 없습니다. 첫 번째 글 작성을 시작합니다.")
            
        # 2. 중복 없는 콘텐츠 생성 (히스토리 주입)
        mdx_content = generate_blog_content(history)
        
        # 3. 파일 저장
        save_mdx_file(mdx_content)
        
        # 4. Git 자동화 실행
        git_push_all()
        
    except Exception as e:
        print(f"💥 프로그램 실행 실패: {e}", file=sys.stderr)