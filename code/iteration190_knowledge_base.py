#!/usr/bin/env python3
"""
Server Init - Iteration 190: Knowledge Base Platform
Платформа базы знаний

Функционал:
- Article Management - управление статьями
- Category Organization - организация категорий
- Full-Text Search - полнотекстовый поиск
- Version History - история версий
- Content Review - ревью контента
- Analytics - аналитика использования
- Access Control - контроль доступа
- Export/Import - экспорт/импорт
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import hashlib


class ArticleStatus(Enum):
    """Статус статьи"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class ContentType(Enum):
    """Тип контента"""
    ARTICLE = "article"
    TUTORIAL = "tutorial"
    FAQ = "faq"
    TROUBLESHOOTING = "troubleshooting"
    REFERENCE = "reference"
    HOW_TO = "how_to"


class ArticleVisibility(Enum):
    """Видимость статьи"""
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    PRIVATE = "private"


@dataclass
class Author:
    """Автор"""
    author_id: str
    name: str = ""
    email: str = ""
    
    # Stats
    articles_count: int = 0
    total_views: int = 0
    
    # Role
    role: str = "contributor"  # contributor, editor, admin


@dataclass
class Category:
    """Категория"""
    category_id: str
    name: str = ""
    slug: str = ""
    description: str = ""
    
    # Hierarchy
    parent_id: Optional[str] = None
    path: str = ""
    level: int = 0
    
    # Stats
    article_count: int = 0
    
    # Icon
    icon: str = "📁"


@dataclass
class Tag:
    """Тег"""
    tag_id: str
    name: str = ""
    slug: str = ""
    
    # Stats
    usage_count: int = 0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ArticleVersion:
    """Версия статьи"""
    version_id: str
    article_id: str
    version_number: int = 1
    
    # Content
    title: str = ""
    content: str = ""
    summary: str = ""
    
    # Author
    author_id: str = ""
    
    # Changes
    change_description: str = ""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    content_hash: str = ""
    
    def compute_hash(self):
        """Вычисление хеша контента"""
        content = f"{self.title}|{self.content}|{self.summary}"
        self.content_hash = hashlib.md5(content.encode()).hexdigest()[:12]


@dataclass
class Article:
    """Статья"""
    article_id: str
    
    # Content
    title: str = ""
    slug: str = ""
    content: str = ""
    summary: str = ""
    
    # Type
    content_type: ContentType = ContentType.ARTICLE
    status: ArticleStatus = ArticleStatus.DRAFT
    visibility: ArticleVisibility = ArticleVisibility.INTERNAL
    
    # Organization
    category_id: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Author
    author_id: str = ""
    last_editor_id: str = ""
    
    # Versions
    current_version: int = 1
    versions: List[str] = field(default_factory=list)  # version_ids
    
    # Analytics
    view_count: int = 0
    helpful_votes: int = 0
    not_helpful_votes: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    
    # Related
    related_articles: List[str] = field(default_factory=list)
    
    @property
    def helpfulness_score(self) -> float:
        total = self.helpful_votes + self.not_helpful_votes
        return (self.helpful_votes / total * 100) if total > 0 else 0


@dataclass
class SearchResult:
    """Результат поиска"""
    article_id: str
    title: str = ""
    summary: str = ""
    score: float = 0.0
    highlights: List[str] = field(default_factory=list)


@dataclass
class ReviewRequest:
    """Запрос на ревью"""
    request_id: str
    article_id: str
    
    # Requester
    requester_id: str = ""
    reviewer_id: Optional[str] = None
    
    # Status
    status: str = "pending"  # pending, in_review, approved, rejected
    
    # Comments
    comments: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class ArticleStore:
    """Хранилище статей"""
    
    def __init__(self):
        self.articles: Dict[str, Article] = {}
        self.versions: Dict[str, ArticleVersion] = {}
        
    def create(self, title: str, content: str, author_id: str,
              category_id: str = "", content_type: ContentType = ContentType.ARTICLE) -> Article:
        """Создание статьи"""
        article_id = f"article_{uuid.uuid4().hex[:8]}"
        slug = title.lower().replace(" ", "-")[:50]
        
        article = Article(
            article_id=article_id,
            title=title,
            slug=slug,
            content=content,
            summary=content[:200] + "..." if len(content) > 200 else content,
            content_type=content_type,
            category_id=category_id,
            author_id=author_id,
            last_editor_id=author_id
        )
        
        # Create initial version
        version = self._create_version(article, author_id, "Initial version")
        article.versions.append(version.version_id)
        
        self.articles[article_id] = article
        return article
        
    def update(self, article_id: str, title: str = None, content: str = None,
              editor_id: str = "", change_description: str = "") -> Optional[Article]:
        """Обновление статьи"""
        article = self.articles.get(article_id)
        if not article:
            return None
            
        if title:
            article.title = title
        if content:
            article.content = content
            article.summary = content[:200] + "..." if len(content) > 200 else content
            
        article.last_editor_id = editor_id
        article.updated_at = datetime.now()
        article.current_version += 1
        
        # Create new version
        version = self._create_version(article, editor_id, change_description)
        article.versions.append(version.version_id)
        
        return article
        
    def _create_version(self, article: Article, author_id: str, 
                       description: str) -> ArticleVersion:
        """Создание версии"""
        version = ArticleVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            article_id=article.article_id,
            version_number=article.current_version,
            title=article.title,
            content=article.content,
            summary=article.summary,
            author_id=author_id,
            change_description=description
        )
        version.compute_hash()
        self.versions[version.version_id] = version
        return version
        
    def get(self, article_id: str) -> Optional[Article]:
        """Получение статьи"""
        return self.articles.get(article_id)
        
    def get_version(self, version_id: str) -> Optional[ArticleVersion]:
        """Получение версии"""
        return self.versions.get(version_id)
        
    def publish(self, article_id: str) -> bool:
        """Публикация статьи"""
        article = self.articles.get(article_id)
        if article:
            article.status = ArticleStatus.PUBLISHED
            article.published_at = datetime.now()
            return True
        return False


class CategoryManager:
    """Менеджер категорий"""
    
    def __init__(self):
        self.categories: Dict[str, Category] = {}
        
    def create(self, name: str, parent_id: str = None, 
              description: str = "", icon: str = "📁") -> Category:
        """Создание категории"""
        category_id = f"cat_{uuid.uuid4().hex[:8]}"
        slug = name.lower().replace(" ", "-")
        
        # Calculate path and level
        if parent_id and parent_id in self.categories:
            parent = self.categories[parent_id]
            path = f"{parent.path}/{slug}"
            level = parent.level + 1
        else:
            path = f"/{slug}"
            level = 0
            
        category = Category(
            category_id=category_id,
            name=name,
            slug=slug,
            description=description,
            parent_id=parent_id,
            path=path,
            level=level,
            icon=icon
        )
        
        self.categories[category_id] = category
        return category
        
    def get_tree(self) -> List[Dict[str, Any]]:
        """Получение дерева категорий"""
        root_categories = [c for c in self.categories.values() if not c.parent_id]
        
        def build_tree(category: Category) -> Dict[str, Any]:
            children = [
                c for c in self.categories.values() 
                if c.parent_id == category.category_id
            ]
            return {
                "category": category,
                "children": [build_tree(c) for c in children]
            }
            
        return [build_tree(c) for c in root_categories]


class SearchEngine:
    """Поисковый движок"""
    
    def __init__(self, article_store: ArticleStore):
        self.article_store = article_store
        self.search_history: List[Dict[str, Any]] = []
        
    def search(self, query: str, filters: Dict[str, Any] = None) -> List[SearchResult]:
        """Полнотекстовый поиск"""
        query_lower = query.lower()
        results = []
        
        for article in self.article_store.articles.values():
            if article.status != ArticleStatus.PUBLISHED:
                continue
                
            # Apply filters
            if filters:
                if "category_id" in filters and article.category_id != filters["category_id"]:
                    continue
                if "content_type" in filters and article.content_type != filters["content_type"]:
                    continue
                    
            # Calculate score
            score = 0
            highlights = []
            
            # Title match (highest weight)
            if query_lower in article.title.lower():
                score += 10
                highlights.append(f"Title: {article.title}")
                
            # Summary match
            if query_lower in article.summary.lower():
                score += 5
                highlights.append(f"Summary: ...{query}...")
                
            # Content match
            content_lower = article.content.lower()
            if query_lower in content_lower:
                count = content_lower.count(query_lower)
                score += count
                highlights.append(f"Content: {count} matches")
                
            # Tag match
            for tag in article.tags:
                if query_lower in tag.lower():
                    score += 3
                    highlights.append(f"Tag: {tag}")
                    
            if score > 0:
                results.append(SearchResult(
                    article_id=article.article_id,
                    title=article.title,
                    summary=article.summary,
                    score=score,
                    highlights=highlights
                ))
                
        # Log search
        self.search_history.append({
            "query": query,
            "results_count": len(results),
            "timestamp": datetime.now()
        })
        
        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)
        return results


class ReviewManager:
    """Менеджер ревью"""
    
    def __init__(self, article_store: ArticleStore):
        self.article_store = article_store
        self.requests: Dict[str, ReviewRequest] = {}
        
    def request_review(self, article_id: str, requester_id: str) -> ReviewRequest:
        """Запрос ревью"""
        article = self.article_store.get(article_id)
        if article:
            article.status = ArticleStatus.PENDING_REVIEW
            
        request = ReviewRequest(
            request_id=f"review_{uuid.uuid4().hex[:8]}",
            article_id=article_id,
            requester_id=requester_id
        )
        
        self.requests[request.request_id] = request
        return request
        
    def approve(self, request_id: str, reviewer_id: str, 
               comments: str = "") -> bool:
        """Одобрение"""
        request = self.requests.get(request_id)
        if not request:
            return False
            
        request.status = "approved"
        request.reviewer_id = reviewer_id
        request.comments = comments
        request.completed_at = datetime.now()
        
        # Publish article
        self.article_store.publish(request.article_id)
        
        return True
        
    def reject(self, request_id: str, reviewer_id: str, 
              comments: str = "") -> bool:
        """Отклонение"""
        request = self.requests.get(request_id)
        if not request:
            return False
            
        request.status = "rejected"
        request.reviewer_id = reviewer_id
        request.comments = comments
        request.completed_at = datetime.now()
        
        # Return to draft
        article = self.article_store.get(request.article_id)
        if article:
            article.status = ArticleStatus.DRAFT
            
        return True


class AnalyticsTracker:
    """Трекер аналитики"""
    
    def __init__(self, article_store: ArticleStore):
        self.article_store = article_store
        self.page_views: List[Dict[str, Any]] = []
        self.feedback: List[Dict[str, Any]] = []
        
    def track_view(self, article_id: str, user_id: str = ""):
        """Отслеживание просмотра"""
        article = self.article_store.get(article_id)
        if article:
            article.view_count += 1
            
        self.page_views.append({
            "article_id": article_id,
            "user_id": user_id,
            "timestamp": datetime.now()
        })
        
    def track_feedback(self, article_id: str, helpful: bool, user_id: str = ""):
        """Отслеживание обратной связи"""
        article = self.article_store.get(article_id)
        if article:
            if helpful:
                article.helpful_votes += 1
            else:
                article.not_helpful_votes += 1
                
        self.feedback.append({
            "article_id": article_id,
            "helpful": helpful,
            "user_id": user_id,
            "timestamp": datetime.now()
        })
        
    def get_popular_articles(self, limit: int = 10) -> List[Article]:
        """Популярные статьи"""
        articles = list(self.article_store.articles.values())
        articles.sort(key=lambda a: a.view_count, reverse=True)
        return articles[:limit]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        articles = list(self.article_store.articles.values())
        published = [a for a in articles if a.status == ArticleStatus.PUBLISHED]
        
        return {
            "total_articles": len(articles),
            "published": len(published),
            "total_views": sum(a.view_count for a in articles),
            "avg_helpfulness": sum(a.helpfulness_score for a in published) / len(published) if published else 0
        }


class KnowledgeBasePlatform:
    """Платформа базы знаний"""
    
    def __init__(self):
        self.article_store = ArticleStore()
        self.category_manager = CategoryManager()
        self.search_engine = SearchEngine(self.article_store)
        self.review_manager = ReviewManager(self.article_store)
        self.analytics = AnalyticsTracker(self.article_store)
        self.authors: Dict[str, Author] = {}
        self.tags: Dict[str, Tag] = {}
        
    def create_author(self, name: str, email: str, role: str = "contributor") -> Author:
        """Создание автора"""
        author = Author(
            author_id=f"author_{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            role=role
        )
        self.authors[author.author_id] = author
        return author
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика платформы"""
        analytics_stats = self.analytics.get_statistics()
        
        return {
            **analytics_stats,
            "categories": len(self.category_manager.categories),
            "authors": len(self.authors),
            "tags": len(self.tags),
            "pending_reviews": len([r for r in self.review_manager.requests.values() if r.status == "pending"])
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 190: Knowledge Base Platform")
    print("=" * 60)
    
    platform = KnowledgeBasePlatform()
    print("✓ Knowledge Base Platform created")
    
    # Create authors
    print("\n👤 Creating Authors...")
    
    authors = [
        platform.create_author("Alice Developer", "alice@example.com", "admin"),
        platform.create_author("Bob Engineer", "bob@example.com", "editor"),
        platform.create_author("Charlie Writer", "charlie@example.com", "contributor"),
    ]
    
    for author in authors:
        print(f"  📝 {author.name} ({author.role})")
        
    # Create categories
    print("\n📁 Creating Categories...")
    
    getting_started = platform.category_manager.create("Getting Started", icon="🚀")
    tutorials = platform.category_manager.create("Tutorials", icon="📚")
    api_docs = platform.category_manager.create("API Documentation", icon="🔧")
    troubleshooting = platform.category_manager.create("Troubleshooting", icon="🔍")
    
    # Sub-categories
    platform.category_manager.create("Quick Start", getting_started.category_id, icon="⚡")
    platform.category_manager.create("Installation", getting_started.category_id, icon="💿")
    
    for cat in platform.category_manager.categories.values():
        indent = "  " * (cat.level + 1)
        print(f"{indent}{cat.icon} {cat.name}")
        
    # Create articles
    print("\n📄 Creating Articles...")
    
    sample_articles = [
        ("Getting Started Guide", "This comprehensive guide will help you get started with our platform. Learn the basics and start building today.", ContentType.TUTORIAL),
        ("API Authentication", "Learn how to authenticate your API requests using tokens, OAuth, and API keys.", ContentType.REFERENCE),
        ("Common Error Codes", "A reference guide to common error codes and their solutions.", ContentType.TROUBLESHOOTING),
        ("Best Practices", "Follow these best practices to build scalable and maintainable applications.", ContentType.ARTICLE),
        ("Webhook Integration", "How to set up and configure webhooks for real-time notifications.", ContentType.HOW_TO),
        ("Rate Limiting FAQ", "Frequently asked questions about rate limiting and quotas.", ContentType.FAQ),
        ("Database Configuration", "Step-by-step guide to configure your database connection.", ContentType.TUTORIAL),
        ("Security Checklist", "Essential security checks for production deployments.", ContentType.REFERENCE),
    ]
    
    articles = []
    for title, content, ctype in sample_articles:
        author = random.choice(authors)
        category = random.choice(list(platform.category_manager.categories.values()))
        
        article = platform.article_store.create(
            title=title,
            content=content * 10,  # Longer content
            author_id=author.author_id,
            category_id=category.category_id,
            content_type=ctype
        )
        
        # Add tags
        article.tags = random.sample(
            ["api", "security", "performance", "database", "authentication", "getting-started"],
            k=random.randint(1, 3)
        )
        
        articles.append(article)
        print(f"  📝 {article.title} ({article.content_type.value})")
        
    # Publish some articles
    print("\n✅ Publishing Articles...")
    
    for article in articles[:5]:
        platform.article_store.publish(article.article_id)
        print(f"  ✓ Published: {article.title}")
        
    # Simulate views and feedback
    print("\n📈 Simulating User Activity...")
    
    for article in articles:
        views = random.randint(10, 500)
        for _ in range(views):
            platform.analytics.track_view(article.article_id)
            
        helpful = random.randint(5, 50)
        not_helpful = random.randint(0, 10)
        
        for _ in range(helpful):
            platform.analytics.track_feedback(article.article_id, True)
        for _ in range(not_helpful):
            platform.analytics.track_feedback(article.article_id, False)
            
    print(f"  Simulated {sum(a.view_count for a in articles)} total views")
    
    # Search
    print("\n🔍 Search Results:")
    
    queries = ["api", "security", "getting started"]
    
    for query in queries:
        results = platform.search_engine.search(query)
        print(f"\n  Query: '{query}' - {len(results)} results")
        for result in results[:3]:
            print(f"    📄 {result.title} (score: {result.score:.1f})")
            
    # Popular articles
    print("\n🌟 Most Popular Articles:")
    
    popular = platform.analytics.get_popular_articles(5)
    
    print("\n  ┌─────────────────────────────────────────┬───────┬─────────┬───────────┐")
    print("  │ Article                                 │ Views │ Helpful │ Score     │")
    print("  ├─────────────────────────────────────────┼───────┼─────────┼───────────┤")
    
    for article in popular:
        title = article.title[:39].ljust(39)
        views = str(article.view_count).rjust(5)
        helpful = str(article.helpful_votes).rjust(7)
        score = f"{article.helpfulness_score:.0f}%".rjust(9)
        print(f"  │ {title} │ {views} │ {helpful} │ {score} │")
        
    print("  └─────────────────────────────────────────┴───────┴─────────┴───────────┘")
    
    # Version history
    print("\n📚 Version History (Sample):")
    
    sample_article = articles[0]
    
    # Make some updates
    platform.article_store.update(
        sample_article.article_id,
        content=sample_article.content + " Updated content.",
        editor_id=authors[1].author_id,
        change_description="Added more details"
    )
    
    platform.article_store.update(
        sample_article.article_id,
        title=sample_article.title + " (v2)",
        editor_id=authors[0].author_id,
        change_description="Updated title"
    )
    
    print(f"\n  Article: {sample_article.title}")
    print(f"  Current Version: {sample_article.current_version}")
    print("\n  Versions:")
    
    for version_id in sample_article.versions:
        version = platform.article_store.get_version(version_id)
        if version:
            print(f"    v{version.version_number}: {version.change_description} ({version.created_at.strftime('%H:%M:%S')})")
            
    # Review workflow
    print("\n📋 Review Workflow:")
    
    draft_article = articles[5]
    review_request = platform.review_manager.request_review(
        draft_article.article_id,
        requester_id=authors[2].author_id
    )
    
    print(f"  📝 Review requested for: {draft_article.title}")
    print(f"  Status: {review_request.status}")
    
    # Approve
    platform.review_manager.approve(
        review_request.request_id,
        reviewer_id=authors[0].author_id,
        comments="Great article! Approved."
    )
    
    print(f"  ✅ Approved by: {authors[0].name}")
    print(f"  Article status: {draft_article.status.value}")
    
    # Content breakdown
    print("\n📊 Content Breakdown:")
    
    by_type = {}
    by_status = {}
    
    for article in articles:
        ctype = article.content_type.value
        status = article.status.value
        
        by_type[ctype] = by_type.get(ctype, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1
        
    print("\n  By Content Type:")
    for ctype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * count + "░" * (10 - count)
        print(f"    {ctype:15} [{bar}] {count}")
        
    print("\n  By Status:")
    for status, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
        print(f"    {status:15} {count}")
        
    # Platform statistics
    print("\n📈 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Articles: {stats['total_articles']}")
    print(f"  Published: {stats['published']}")
    print(f"  Categories: {stats['categories']}")
    print(f"  Authors: {stats['authors']}")
    print(f"  Total Views: {stats['total_views']}")
    print(f"  Average Helpfulness: {stats['avg_helpfulness']:.1f}%")
    print(f"  Pending Reviews: {stats['pending_reviews']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Knowledge Base Dashboard                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Articles:                {stats['total_articles']:>12}                        │")
    print(f"│ Published:                     {stats['published']:>12}                        │")
    print(f"│ Total Views:                   {stats['total_views']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Categories:                    {stats['categories']:>12}                        │")
    print(f"│ Authors:                       {stats['authors']:>12}                        │")
    print(f"│ Pending Reviews:               {stats['pending_reviews']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Average Helpfulness:             {stats['avg_helpfulness']:>10.1f}%                   │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Knowledge Base Platform initialized!")
    print("=" * 60)
