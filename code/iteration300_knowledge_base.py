#!/usr/bin/env python3
"""
Server Init - Iteration 300: Knowledge Base Platform
Платформа базы знаний

Функционал:
- Article Management - управление статьями
- Categorization - категоризация
- Search & Discovery - поиск и обнаружение
- Version Control - контроль версий
- Access Management - управление доступом
- Analytics & Metrics - аналитика и метрики
- Feedback System - система обратной связи
- Templates & Workflows - шаблоны и workflow
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import re


class ArticleStatus(Enum):
    """Статус статьи"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class ContentType(Enum):
    """Тип контента"""
    DOCUMENTATION = "documentation"
    TUTORIAL = "tutorial"
    FAQ = "faq"
    TROUBLESHOOTING = "troubleshooting"
    REFERENCE = "reference"
    HOWTO = "howto"


class AccessLevel(Enum):
    """Уровень доступа"""
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"


@dataclass
class ArticleVersion:
    """Версия статьи"""
    version_id: str
    article_id: str
    
    # Version
    version_number: int = 1
    
    # Content
    content: str = ""
    
    # Author
    author: str = ""
    
    # Changes
    change_summary: str = ""
    
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Category:
    """Категория"""
    category_id: str
    name: str
    
    # Hierarchy
    parent_id: Optional[str] = None
    
    # Description
    description: str = ""
    
    # Order
    sort_order: int = 0
    
    # Stats
    article_count: int = 0


@dataclass
class Tag:
    """Тег"""
    tag_id: str
    name: str
    
    # Stats
    usage_count: int = 0


@dataclass
class Feedback:
    """Обратная связь"""
    feedback_id: str
    article_id: str
    
    # Rating
    helpful: bool = True
    rating: int = 5
    
    # Comment
    comment: str = ""
    
    # User
    user: str = ""
    
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Template:
    """Шаблон"""
    template_id: str
    name: str
    
    # Content
    content: str = ""
    
    # Type
    content_type: ContentType = ContentType.DOCUMENTATION
    
    # Sections
    sections: List[str] = field(default_factory=list)


@dataclass
class SearchResult:
    """Результат поиска"""
    article_id: str
    title: str
    excerpt: str
    score: float
    category: str


@dataclass
class Article:
    """Статья"""
    article_id: str
    title: str
    slug: str
    
    # Content
    content: str = ""
    summary: str = ""
    content_type: ContentType = ContentType.DOCUMENTATION
    
    # Status
    status: ArticleStatus = ArticleStatus.DRAFT
    
    # Classification
    category_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Access
    access_level: AccessLevel = AccessLevel.INTERNAL
    
    # Author
    author: str = ""
    contributors: List[str] = field(default_factory=list)
    
    # Versions
    current_version: int = 1
    versions: List[str] = field(default_factory=list)
    
    # Related
    related_articles: List[str] = field(default_factory=list)
    
    # Metadata
    read_time: int = 0  # minutes
    
    # Stats
    views: int = 0
    helpful_votes: int = 0
    not_helpful_votes: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None


class KnowledgeBaseManager:
    """Менеджер Knowledge Base"""
    
    def __init__(self):
        self.articles: Dict[str, Article] = {}
        self.versions: Dict[str, ArticleVersion] = {}
        self.categories: Dict[str, Category] = {}
        self.tags: Dict[str, Tag] = {}
        self.feedback: Dict[str, Feedback] = {}
        self.templates: Dict[str, Template] = {}
        
        # Stats
        self.total_views: int = 0
        self.searches_performed: int = 0
        
    def _generate_slug(self, title: str) -> str:
        """Генерация slug"""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        return slug[:50]
        
    async def create_category(self, name: str, description: str = "",
                             parent_id: Optional[str] = None) -> Category:
        """Создание категории"""
        category = Category(
            category_id=f"cat_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            parent_id=parent_id
        )
        
        self.categories[category.category_id] = category
        return category
        
    async def create_tag(self, name: str) -> Tag:
        """Создание тега"""
        # Check if tag exists
        for tag in self.tags.values():
            if tag.name.lower() == name.lower():
                return tag
                
        tag = Tag(
            tag_id=f"tag_{uuid.uuid4().hex[:8]}",
            name=name
        )
        
        self.tags[tag.tag_id] = tag
        return tag
        
    async def create_article(self, title: str,
                            content: str,
                            content_type: ContentType = ContentType.DOCUMENTATION,
                            author: str = "",
                            category_id: Optional[str] = None,
                            access_level: AccessLevel = AccessLevel.INTERNAL) -> Article:
        """Создание статьи"""
        article = Article(
            article_id=f"kb_{uuid.uuid4().hex[:8]}",
            title=title,
            slug=self._generate_slug(title),
            content=content,
            summary=content[:200] + "..." if len(content) > 200 else content,
            content_type=content_type,
            author=author,
            category_id=category_id,
            access_level=access_level
        )
        
        # Calculate read time (average 200 words per minute)
        word_count = len(content.split())
        article.read_time = max(1, word_count // 200)
        
        # Create initial version
        version = await self._create_version(article.article_id, content, author, "Initial version")
        article.versions.append(version.version_id)
        
        # Update category count
        if category_id and category_id in self.categories:
            self.categories[category_id].article_count += 1
            
        self.articles[article.article_id] = article
        return article
        
    async def _create_version(self, article_id: str, content: str,
                             author: str, change_summary: str) -> ArticleVersion:
        """Создание версии"""
        article = self.articles.get(article_id)
        version_number = article.current_version if article else 1
        
        version = ArticleVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            article_id=article_id,
            version_number=version_number,
            content=content,
            author=author,
            change_summary=change_summary
        )
        
        self.versions[version.version_id] = version
        return version
        
    async def update_article(self, article_id: str,
                            title: Optional[str] = None,
                            content: Optional[str] = None,
                            editor: str = "",
                            change_summary: str = "") -> bool:
        """Обновление статьи"""
        article = self.articles.get(article_id)
        if not article:
            return False
            
        if title:
            article.title = title
            article.slug = self._generate_slug(title)
            
        if content:
            article.content = content
            article.summary = content[:200] + "..." if len(content) > 200 else content
            article.read_time = max(1, len(content.split()) // 200)
            
            # Create new version
            article.current_version += 1
            version = await self._create_version(article_id, content, editor, change_summary)
            article.versions.append(version.version_id)
            
        if editor and editor not in article.contributors:
            article.contributors.append(editor)
            
        article.updated_at = datetime.now()
        
        return True
        
    async def publish_article(self, article_id: str) -> bool:
        """Публикация статьи"""
        article = self.articles.get(article_id)
        if not article:
            return False
            
        article.status = ArticleStatus.PUBLISHED
        article.published_at = datetime.now()
        
        return True
        
    async def add_tags(self, article_id: str, tag_names: List[str]) -> bool:
        """Добавление тегов"""
        article = self.articles.get(article_id)
        if not article:
            return False
            
        for tag_name in tag_names:
            tag = await self.create_tag(tag_name)
            
            if tag.tag_id not in article.tags:
                article.tags.append(tag.tag_id)
                tag.usage_count += 1
                
        return True
        
    async def view_article(self, article_id: str) -> Optional[Article]:
        """Просмотр статьи"""
        article = self.articles.get(article_id)
        if not article or article.status != ArticleStatus.PUBLISHED:
            return None
            
        article.views += 1
        self.total_views += 1
        
        return article
        
    async def search(self, query: str, category_id: Optional[str] = None,
                    content_type: Optional[ContentType] = None,
                    limit: int = 10) -> List[SearchResult]:
        """Поиск статей"""
        self.searches_performed += 1
        results = []
        
        query_lower = query.lower()
        query_words = query_lower.split()
        
        for article in self.articles.values():
            if article.status != ArticleStatus.PUBLISHED:
                continue
                
            if category_id and article.category_id != category_id:
                continue
                
            if content_type and article.content_type != content_type:
                continue
                
            # Calculate relevance score
            score = 0.0
            
            title_lower = article.title.lower()
            content_lower = article.content.lower()
            
            for word in query_words:
                if word in title_lower:
                    score += 10.0
                if word in content_lower:
                    score += 1.0 * content_lower.count(word)
                    
            if score > 0:
                # Get excerpt
                excerpt = article.summary
                
                category_name = ""
                if article.category_id and article.category_id in self.categories:
                    category_name = self.categories[article.category_id].name
                    
                results.append(SearchResult(
                    article_id=article.article_id,
                    title=article.title,
                    excerpt=excerpt,
                    score=score,
                    category=category_name
                ))
                
        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:limit]
        
    async def add_feedback(self, article_id: str, helpful: bool,
                          rating: int = 5, comment: str = "",
                          user: str = "") -> Optional[Feedback]:
        """Добавление обратной связи"""
        article = self.articles.get(article_id)
        if not article:
            return None
            
        feedback = Feedback(
            feedback_id=f"fb_{uuid.uuid4().hex[:8]}",
            article_id=article_id,
            helpful=helpful,
            rating=rating,
            comment=comment,
            user=user
        )
        
        if helpful:
            article.helpful_votes += 1
        else:
            article.not_helpful_votes += 1
            
        self.feedback[feedback.feedback_id] = feedback
        return feedback
        
    async def create_template(self, name: str, content_type: ContentType,
                             sections: List[str]) -> Template:
        """Создание шаблона"""
        content = "\n\n".join([f"## {section}\n\n[Content for {section}]" for section in sections])
        
        template = Template(
            template_id=f"tpl_{uuid.uuid4().hex[:8]}",
            name=name,
            content=content,
            content_type=content_type,
            sections=sections
        )
        
        self.templates[template.template_id] = template
        return template
        
    async def get_popular_articles(self, limit: int = 10) -> List[Article]:
        """Получение популярных статей"""
        published = [a for a in self.articles.values() if a.status == ArticleStatus.PUBLISHED]
        return sorted(published, key=lambda x: x.views, reverse=True)[:limit]
        
    async def get_recent_articles(self, limit: int = 10) -> List[Article]:
        """Получение недавних статей"""
        published = [a for a in self.articles.values() if a.status == ArticleStatus.PUBLISHED]
        return sorted(published, key=lambda x: x.published_at or x.created_at, reverse=True)[:limit]
        
    def get_article_stats(self, article_id: str) -> Dict[str, Any]:
        """Статистика статьи"""
        article = self.articles.get(article_id)
        if not article:
            return {}
            
        total_votes = article.helpful_votes + article.not_helpful_votes
        helpful_rate = (article.helpful_votes / total_votes * 100) if total_votes > 0 else 0
        
        return {
            "article_id": article_id,
            "title": article.title,
            "views": article.views,
            "helpful_votes": article.helpful_votes,
            "not_helpful_votes": article.not_helpful_votes,
            "helpful_rate": helpful_rate,
            "version_count": len(article.versions),
            "contributors": len(article.contributors) + 1
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        published = sum(1 for a in self.articles.values() if a.status == ArticleStatus.PUBLISHED)
        draft = sum(1 for a in self.articles.values() if a.status == ArticleStatus.DRAFT)
        
        type_counts = {}
        for ct in ContentType:
            type_counts[ct.value] = sum(1 for a in self.articles.values() if a.content_type == ct)
            
        total_helpful = sum(a.helpful_votes for a in self.articles.values())
        total_not_helpful = sum(a.not_helpful_votes for a in self.articles.values())
        
        avg_read_time = sum(a.read_time for a in self.articles.values()) / max(len(self.articles), 1)
        
        return {
            "total_articles": len(self.articles),
            "published": published,
            "draft": draft,
            "categories": len(self.categories),
            "tags": len(self.tags),
            "total_views": self.total_views,
            "searches": self.searches_performed,
            "feedback_count": len(self.feedback),
            "helpful_votes": total_helpful,
            "not_helpful_votes": total_not_helpful,
            "type_breakdown": type_counts,
            "avg_read_time": avg_read_time,
            "versions_created": len(self.versions)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 300: Knowledge Base Platform")
    print("=" * 60)
    
    manager = KnowledgeBaseManager()
    print("✓ Knowledge Base Manager created")
    
    # Create categories
    print("\n📁 Creating Categories...")
    
    categories_data = [
        ("Getting Started", "Introductory guides and tutorials"),
        ("API Reference", "API documentation and specifications"),
        ("Troubleshooting", "Common issues and solutions"),
        ("Best Practices", "Recommended approaches and patterns"),
        ("Security", "Security guidelines and policies"),
        ("Administration", "System administration guides")
    ]
    
    categories = []
    for name, desc in categories_data:
        category = await manager.create_category(name, desc)
        categories.append(category)
        print(f"  📁 {name}")
        
    # Create templates
    print("\n📝 Creating Templates...")
    
    templates_data = [
        ("Documentation Template", ContentType.DOCUMENTATION, 
         ["Overview", "Prerequisites", "Installation", "Configuration", "Usage", "Troubleshooting"]),
        ("Tutorial Template", ContentType.TUTORIAL,
         ["Introduction", "Prerequisites", "Step 1", "Step 2", "Step 3", "Conclusion"]),
        ("FAQ Template", ContentType.FAQ,
         ["Question 1", "Question 2", "Question 3", "Related Topics"]),
        ("Troubleshooting Template", ContentType.TROUBLESHOOTING,
         ["Problem", "Symptoms", "Cause", "Solution", "Prevention"])
    ]
    
    for name, c_type, sections in templates_data:
        template = await manager.create_template(name, c_type, sections)
        print(f"  📝 {name} ({len(sections)} sections)")
        
    # Create articles
    print("\n📄 Creating Articles...")
    
    articles_data = [
        ("Getting Started with Platform API", ContentType.DOCUMENTATION, 0,
         """This guide will help you get started with the Platform API.

## Overview
The Platform API provides programmatic access to all platform features.

## Authentication
All API requests require authentication using API keys or OAuth tokens.

## Making Your First Request
Use the following endpoint to test connectivity:
GET /api/v1/health

## Rate Limiting
The API enforces rate limits of 1000 requests per hour.""",
         ["api", "authentication", "quickstart"]),
         
        ("How to Configure Webhooks", ContentType.TUTORIAL, 0,
         """Learn how to set up webhooks for real-time notifications.

## Prerequisites
- API access enabled
- Endpoint URL ready

## Step 1: Create Webhook
Navigate to Settings > Webhooks and click Create.

## Step 2: Configure Events
Select the events you want to receive notifications for.

## Step 3: Test Webhook
Use the Test button to verify your endpoint.""",
         ["webhooks", "integration", "notifications"]),
         
        ("Common API Errors and Solutions", ContentType.TROUBLESHOOTING, 2,
         """This article covers common API errors and how to resolve them.

## 401 Unauthorized
Your API key is invalid or expired. Generate a new key.

## 429 Too Many Requests
You've exceeded the rate limit. Implement exponential backoff.

## 500 Internal Server Error
Server-side issue. Check status page and retry later.""",
         ["api", "errors", "troubleshooting"]),
         
        ("Security Best Practices", ContentType.REFERENCE, 4,
         """Follow these security best practices to protect your application.

## API Key Management
- Rotate keys regularly
- Use environment variables
- Never commit keys to code

## Authentication
- Use OAuth 2.0 when possible
- Implement MFA for admin accounts

## Network Security
- Use TLS 1.3
- Implement IP allowlisting""",
         ["security", "best-practices", "authentication"]),
         
        ("Database Connection Guide", ContentType.HOWTO, 3,
         """Learn how to connect to the platform database.

## Connection String
Use the following format:
postgresql://user:password@host:port/database

## Connection Pooling
Configure connection pooling for optimal performance.

## SSL Configuration
Enable SSL for secure connections.""",
         ["database", "connection", "postgresql"]),
         
        ("Frequently Asked Questions", ContentType.FAQ, 0,
         """Answers to frequently asked questions.

## What is the API rate limit?
The default rate limit is 1000 requests per hour.

## How do I reset my password?
Use the forgot password link on the login page.

## Can I export my data?
Yes, use the export feature in Settings.""",
         ["faq", "general", "support"])
    ]
    
    articles = []
    for title, c_type, cat_idx, content, tags in articles_data:
        article = await manager.create_article(
            title, content, c_type,
            author="tech-writer@company.com",
            category_id=categories[cat_idx].category_id
        )
        articles.append(article)
        
        await manager.add_tags(article.article_id, tags)
        
        type_icons = {
            ContentType.DOCUMENTATION: "📚",
            ContentType.TUTORIAL: "📖",
            ContentType.FAQ: "❓",
            ContentType.TROUBLESHOOTING: "🔧",
            ContentType.REFERENCE: "📋",
            ContentType.HOWTO: "🎯"
        }
        icon = type_icons.get(c_type, "📄")
        
        print(f"\n  {icon} {title}")
        print(f"     Type: {c_type.value} | Tags: {', '.join(tags)}")
        print(f"     Read time: {article.read_time} min")
        
    # Publish articles
    print("\n📢 Publishing Articles...")
    
    for article in articles:
        await manager.publish_article(article.article_id)
        
    print(f"  ✅ Published {len(articles)} articles")
    
    # Update an article
    print("\n✏️ Updating Article...")
    
    await manager.update_article(
        articles[0].article_id,
        content=articles[0].content + "\n\n## New Section\nAdditional content added.",
        editor="senior-writer@company.com",
        change_summary="Added new section"
    )
    
    print(f"  ✏️ Updated: {articles[0].title}")
    print(f"     Version: {articles[0].current_version}")
    
    # Simulate views
    print("\n👀 Simulating Views...")
    
    for article in articles:
        view_count = random.randint(50, 500)
        for _ in range(view_count):
            await manager.view_article(article.article_id)
            
    print(f"  👀 Total views: {manager.total_views}")
    
    # Add feedback
    print("\n💬 Adding Feedback...")
    
    for article in articles:
        feedback_count = random.randint(5, 20)
        for _ in range(feedback_count):
            helpful = random.random() > 0.2  # 80% helpful
            rating = random.randint(3, 5) if helpful else random.randint(1, 3)
            await manager.add_feedback(
                article.article_id,
                helpful=helpful,
                rating=rating,
                comment="Great article!" if helpful else "Needs more detail",
                user=f"user{random.randint(1, 100)}@company.com"
            )
            
    print(f"  💬 Added {len(manager.feedback)} feedback entries")
    
    # Search
    print("\n🔍 Searching Articles...")
    
    search_queries = ["API", "security", "database", "webhook"]
    
    for query in search_queries:
        results = await manager.search(query)
        print(f"\n  🔍 '{query}': {len(results)} results")
        for result in results[:3]:
            print(f"     📄 {result.title} (score: {result.score:.1f})")
            
    # Popular articles
    print("\n🌟 Popular Articles:")
    
    popular = await manager.get_popular_articles(5)
    
    for i, article in enumerate(popular, 1):
        helpful_rate = (article.helpful_votes / max(article.helpful_votes + article.not_helpful_votes, 1)) * 100
        print(f"  {i}. {article.title}")
        print(f"     👀 {article.views} views | 👍 {helpful_rate:.0f}% helpful")
        
    # Article statistics table
    print("\n📊 Article Statistics:")
    
    print("\n  ┌────────────────────────────────────┬────────┬────────┬────────┬─────────┐")
    print("  │ Article                            │ Views  │ 👍     │ 👎     │ Rate    │")
    print("  ├────────────────────────────────────┼────────┼────────┼────────┼─────────┤")
    
    for article in articles:
        stats = manager.get_article_stats(article.article_id)
        
        title = article.title[:34].ljust(34)
        views = str(stats['views']).ljust(6)
        helpful = str(stats['helpful_votes']).ljust(6)
        not_helpful = str(stats['not_helpful_votes']).ljust(6)
        rate = f"{stats['helpful_rate']:.0f}%".ljust(7)
        
        print(f"  │ {title} │ {views} │ {helpful} │ {not_helpful} │ {rate} │")
        
    print("  └────────────────────────────────────┴────────┴────────┴────────┴─────────┘")
    
    # Category distribution
    print("\n📁 Category Distribution:")
    
    for category in categories:
        count = category.article_count
        if count > 0:
            bar = "█" * count + "░" * (6 - count)
            print(f"  {category.name[:20].ljust(20)} [{bar}] {count}")
            
    # Content type distribution
    print("\n📊 Content Type Distribution:")
    
    stats = manager.get_statistics()
    
    type_icons = {
        "documentation": "📚",
        "tutorial": "📖",
        "faq": "❓",
        "troubleshooting": "🔧",
        "reference": "📋",
        "howto": "🎯"
    }
    
    for c_type, count in stats['type_breakdown'].items():
        if count > 0:
            icon = type_icons.get(c_type, "📄")
            bar = "█" * count + "░" * (6 - count)
            print(f"  {icon} {c_type[:15].ljust(15)} [{bar}] {count}")
            
    # Tag cloud
    print("\n🏷️ Popular Tags:")
    
    popular_tags = sorted(manager.tags.values(), key=lambda x: x.usage_count, reverse=True)[:10]
    tag_str = "  "
    for tag in popular_tags:
        tag_str += f"[{tag.name}:{tag.usage_count}] "
        
    print(tag_str)
    
    # Statistics
    print("\n📊 Knowledge Base Statistics:")
    
    print(f"\n  Total Articles: {stats['total_articles']}")
    print(f"    Published: {stats['published']}")
    print(f"    Draft: {stats['draft']}")
    print(f"\n  Categories: {stats['categories']}")
    print(f"  Tags: {stats['tags']}")
    print(f"\n  Total Views: {stats['total_views']}")
    print(f"  Searches: {stats['searches']}")
    print(f"\n  Feedback: {stats['feedback_count']}")
    print(f"  Helpful Votes: {stats['helpful_votes']}")
    print(f"  Versions Created: {stats['versions_created']}")
    print(f"\n  Avg Read Time: {stats['avg_read_time']:.1f} minutes")
    
    helpful_rate = (stats['helpful_votes'] / max(stats['helpful_votes'] + stats['not_helpful_votes'], 1)) * 100
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Knowledge Base Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Articles:                {stats['total_articles']:>12}                        │")
    print(f"│ Published Articles:            {stats['published']:>12}                        │")
    print(f"│ Total Views:                   {stats['total_views']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Helpfulness Rate:              {helpful_rate:>11.1f}%                        │")
    print(f"│ Total Feedback:                {stats['feedback_count']:>12}                        │")
    print(f"│ Searches Performed:            {stats['searches']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("🎉 Knowledge Base Platform initialized!")
    print("🎉 Iteration 300 completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
