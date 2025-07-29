#!/usr/bin/env python3
"""
Test script for the consolidated Bible downloader.
"""

import asyncio
import logging
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bible_downloader import (
    AsyncBibleDownloader,
    download_bible_async,
    BOOKS,
    BIBLE_TRANSLATIONS,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_single_chapter():
    """Test downloading a single chapter."""
    logger.info("🧪 Testing single chapter download...")
    
    async with AsyncBibleDownloader("NIV", max_concurrent_requests=3) as downloader:
        result = await downloader.download_chapter("Genesis", 1)
        
        if result:
            logger.info(f"✅ Successfully downloaded Genesis 1: {len(result['verses'])} verses")
            logger.info(f"   First verse: {result['verses'][0][:100]}...")
        else:
            logger.error("❌ Failed to download Genesis 1")


async def test_single_book():
    """Test downloading a single book."""
    logger.info("🧪 Testing single book download...")
    
    result = await download_bible_async(
        translation="NIV",
        books=["Philemon"],  # Small book with 1 chapter
        max_concurrent_requests=3,
        max_retries=2,
        retry_delay=1,
        timeout=60
    )
    
    if result:
        logger.info(f"✅ Successfully downloaded Philemon: {len(result)} chapters")
        total_verses = sum(len(chapter['verses']) for chapter in result)
        logger.info(f"   Total verses: {total_verses}")
    else:
        logger.error("❌ Failed to download Philemon")


async def test_multiple_books():
    """Test downloading multiple books in parallel."""
    logger.info("🧪 Testing multiple books download in parallel...")
    
    # Test with small books
    books_to_test = ["Philemon", "Jude", "2 John", "3 John"]  # All have 1 chapter
    
    result = await download_bible_async(
        translation="NIV",
        books=books_to_test,
        max_concurrent_requests=5,
        max_retries=2,
        retry_delay=1,
        timeout=60
    )
    
    if result:
        logger.info(f"✅ Successfully downloaded {len(books_to_test)} books")
        total_chapters = len(result)
        total_verses = sum(len(chapter['verses']) for chapter in result)
        logger.info(f"   Total chapters: {total_chapters}, Total verses: {total_verses}")
    else:
        logger.error("❌ Failed to download multiple books")


async def test_concurrency():
    """Test true concurrency with multiple translations."""
    logger.info("🧪 Testing true concurrency with multiple translations...")
    
    translations = ["NIV", "KJV"]
    books = ["Genesis", "Exodus"]  # First two books
    
    tasks = []
    for translation in translations:
        for book in books:
            task = download_bible_async(
                translation=translation,
                books=[book],
                max_concurrent_requests=3,
                max_retries=2,
                retry_delay=1,
                timeout=60
            )
            tasks.append((translation, book, task))
    
    # Execute all tasks concurrently
    results = []
    for translation, book, task in tasks:
        try:
            result = await task
            results.append((translation, book, result))
        except Exception as e:
            logger.error(f"❌ Error downloading {book} ({translation}): {e}")
            results.append((translation, book, None))
    
    # Process results
    successful = sum(1 for _, _, result in results if result)
    total = len(results)
    logger.info(f"✅ Concurrency test completed: {successful}/{total} successful downloads")


async def main():
    """Run all tests."""
    logger.info("🚀 Starting consolidated Bible downloader tests...")
    
    try:
        await test_single_chapter()
        await test_single_book()
        await test_multiple_books()
        await test_concurrency()
        
        logger.info("✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 