import os
import sys
import re
import time
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
    You are an expert Senior Backend Engineer and a prolific tech blogger. 
    Review the list of previously written blog posts and select a brand new, highly relevant, and deep-dive backend technical topic based on the focus stack.
    The new topic must connect naturally but avoid any duplication.

    [Focus Tech Stack]: {BLOG_TECH_STACK}
    
    [Previous Blog Posts]:
    {history_context}
    
    [STRICT REQUIREMENTS]:
    1. LANGUAGE: The entire post (including title, frontmatter, and body) MUST be written in professional, natural, and fluent English.
    2. TONE & MANNER: Maintain an engaging, authoritative yet accessible 'Senior-to-Peer' developer tone. Use active voice and clear, concise technical terminology. Avoid sounding like a generic AI or textbook.
    3. MDX FRONTMATTER: Include the exact frontmatter block at the very top:
       ---
       title: "Engaging and clear technical title"
       date: "{datetime.now().strftime("%Y-%m-%d")}"
       tags: ["tag1", "tag2"]
       description: "A punchy, 1-2 sentence summary of what the reader will learn."
       ---
    4. STRUCTURE: 
       - Introduction: Hook the reader by stating a real-world problem or architectural challenge.
       - Deep Dive / Core Concept: Explain the mechanism/patterns clearly.
       - Production-Ready Code: Provide fully functional, concrete Java/Spring Boot 4 examples without using lazy placeholders or pseudo-code.
       - Best Practices / Trade-offs: Discuss performance implications, gotchas, or production considerations.
       - Conclusion: Wrap up with a brief summary.
    5. OUTPUT FORMAT: Return ONLY the raw MDX content. Do not include any conversational intros, outros, or markdown code block wrappers (like ```mdx) at the outer level.
    """

    max_retries = 3
    retry_delay = 5  # 초 단위

    for attempt in range(1, max_retries + 1):
        try:
            print(f"🤖 Gemini가 히스토리를 분석하여 다음 연계 주제를 고민하는 중... (시도 {attempt}/{max_retries})")
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            return response.text
        except Exception as e:
            # 503 에러 등이 발생하면 잡아서 대기 후 재시도
            if attempt < max_retries:
                print(f"⚠️ 일시적인 서버 오류 발생: {e}\n⏱️ {retry_delay}초 후 다시 시도합니다...")
                time.sleep(retry_delay)
            else:
                # 최대 재시도 횟수를 넘기면 원래대로 예외 던지기
                raise e

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