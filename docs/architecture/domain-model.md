# Japanese Language Learning Platform - Domain Model

## 1. Core Entities

### 1.1 User Model

```python
class User(AbstractUser):
    """
    Extended user model with Japanese language learning context.
    Uses Django's built-in user fields plus language-specific fields.
    """
    
    # Standard Django user fields
    username: str
    email: str
    first_name: str
    last_name: str
    
    # Language learning profile
    native_language: str  # e.g., "ru" (Russian)
    target_language: str  # e.g., "ja" (Japanese)
    proficiency_level: str  # e.g., "beginner", "intermediate", "advanced"
    
    # Statistics (read-only, computed)
    total_words_learned: int
    total_sentences_learned: int
    total_study_time_minutes: int
    
    # Preferences
    romaji_enabled: bool
    furigana_enabled: bool
    show_kanji_stroke_orders: bool
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_active_at: datetime
```

**Key Decisions:**
- Use Django's `AbstractUser` for standard fields (username, password, etc.)
- No role-based fields (all users are students)
- Single-tenant model: each user is their own tenant
- Profile fields are optional but recommended for better UX

### 1.2 Language Model

```python
class Language(models.Model):
    """
    Represents a language in the system.
    Supports multiple languages for future extensibility.
    """
    
    code = models.CharField(max_length=2, unique=True)  # ISO 639-1
    name_en = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)  # Russian name for our audience
    direction = models.CharField(
        max_length=10,
        choices=[('ltr', 'Left-to-Right'), ('rtl', 'Right-to-Left')]
    )
    script = models.CharField(
        max_length=50,  # e.g., "Hiragana", "Katakana", "Kanji", "Latin"
        blank=True
    )
    is_target_language = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Languages"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} ({self.name_en})"
```

**Key Decisions:**
- ISO 639-1 language codes for standardization
- Russian names for localization to our target audience
- Script field for Japanese-specific handling
- Support for multiple target languages in the future

### 1.3 Word Model

```python
class Word(models.Model):
    """
    Represents a single word with Japanese and optional English meanings.
    Supports multiple scripts and pronunciation variants.
    """
    
    # Japanese representation (primary)
    kana = models.CharField(
        max_length=50,
        help_text="Hiragana or Katakana representation"
    )
    kanji = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Kanji representation (optional)"
    )
    romaji = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Romaji (romanized) representation"
    )
    
    # English representation (optional)
    meaning_en = models.TextField(
        blank=True,
        help_text="English definition or meaning"
    )
    
    # Additional meanings (for polysemous words)
    meanings_en = models.JSONField(
        blank=True,
        default=list,
        help_text="Additional meanings as list of objects with context"
    )
    
    # Pronunciation
    pronunciation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="IPA pronunciation"
    )
    
    # Japanese-specific fields
    furigana = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Furigana pronunciation guide over kanji"
    )
    
    # Word type and category
    word_type = models.CharField(
        max_length=50,
        choices=[
            ('noun', 'Noun'),
            ('verb', 'Verb'),
            ('adjective', 'Adjective'),
            ('adverb', 'Adverb'),
            ('particle', 'Particle'),
            ('conjunction', 'Conjunction'),
            ('interjection', 'Interjection'),
            ('other', 'Other')
        ],
        default='other'
    )
    
    # User association (for user-created words)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_words',
        null=True,
        blank=True,
        help_text="User who created this word (None for imported words)"
    )
    
    # Tags for categorization
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="List of tag strings"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['kanji']),
            models.Index(fields=['roma']),
            models.Index(fields=['tags']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['kanji']
    
    def __str__(self):
        return f"{self.kana} ({self.kanji or 'N/A'})"
```

**Key Decisions:**
- Primary key is word ID, not user ID (shared vocabulary)
- Optional kanji field (some words may only be kana)
- Multiple meanings support for polysemous words
- Tags for flexible categorization
- User association for user-created content only

### 1.4 Sentence Model

```python
class Sentence(models.Model):
    """
    Represents a sentence with Japanese text and optional English translation.
    Supports furigana and multiple sentence types.
    """
    
    # Japanese representation
    text = models.TextField(
        help_text="Japanese text with optional furigana"
    )
    
    # English translation
    translation = models.TextField(
        blank=True,
        help_text="English translation"
    )
    
    # Sentence type
    sentence_type = models.CharField(
        max_length=50,
        choices=[
            ('statement', 'Statement'),
            ('question', 'Question'),
            ('exclamation', 'Exclamation'),
            ('command', 'Command'),
            ('idiom', 'Idiom'),
            ('proverb', 'Proverb'),
            ('other', 'Other')
        ],
        default='statement'
    )
    
    # Context and usage notes
    context = models.TextField(
        blank=True,
        help_text="Context in which this sentence is used"
    )
    
    # Usage examples
    examples = models.JSONField(
        default=list,
        blank=True,
        help_text="List of usage examples with translations"
    )
    
    # Japanese-specific fields
    furigana = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Furigana for complex kanji in sentence"
    )
    
    # User association (for user-created sentences)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_sentences',
        null=True,
        blank=True
    )
    
    # Tags
    tags = models.JSONField(
        default=list,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
        ]
        ordering = ['created_at']
    
    def __str__(self):
        return self.text[:50] + "..." if len(self.text) > 50 else self.text
```

**Key Decisions:**
- `text` field includes furigana inline (e.g., 日本語 (にほんご))
- Rich context field for usage notes
- Multiple example structures for diverse usage
- User association for user-created content

## 2. Collection Models

### 2.1 Collection Base Model

```python
class Collection(models.Model):
    """
    Abstract base class for decks and lists.
    Collections group words and sentences for study.
    """
    
    # Shared fields
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Collection type
    type = models.CharField(
        max_length=20,
        choices=[
            ('deck', 'Deck'),  # Full collection for study
            ('list', 'List'),  # Simple list of items
        ]
    )
    
    # Ownership
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collections'
    )
    
    # Sharing settings
    is_shared = models.BooleanField(
        default=False,
        help_text="Can be read by other users"
    )
    shared_with = models.JSONField(
        default=list,
        blank=True,
        help_text="List of usernames who have read access"
    )
    
    # Statistics
    item_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['owner', 'type']),
        ]
    
    def __str__(self):
        return f"{self.type} '{self.name}' by {self.owner.username}"
```

### 2.2 Deck Model

```python
class Deck(Collection):
    """
    A deck is a structured collection of words/sentences for study.
    Supports various study modes and progression tracking.
    """
    
    # Deck-specific settings
    study_mode = models.CharField(
        max_length=50,
        choices=[
            ('flashcard', 'Flashcards'),
            ('multiple_choice', 'Multiple Choice'),
            ('typing', 'Typing'),
            ('matching', 'Matching'),
            ('mixed', 'Mixed')
        ],
        default='flashcard'
    )
    
    # Progression settings
    show_answer_immediately = models.BooleanField(
        default=False,
        help_text="Show answer immediately after incorrect response"
    )
    randomize = models.BooleanField(
        default=True,
        help_text="Randomize item order"
    )
    
    # Display settings
    show_romaji = models.BooleanField(default=True)
    show_kanji = models.BooleanField(default=True)
    show_furigana = models.BooleanField(default=False)
    show_translations = models.BooleanField(default=True)
    
    # Deck-specific items
    words = models.ManyToManyField(
        Word,
        related_name='decks',
        blank=True,
        through='DeckWord'
    )
    
    sentences = models.ManyToManyField(
        Sentence,
        related_name='decks',
        blank=True,
        through='DeckSentence'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Decks"
        indexes = [
            models.Index(fields=['owner']),
        ]
    
    def __str__(self):
        return f"Deck '{self.name}'"
    
    @property
    def total_items(self):
        return self.words.count() + self.sentences.count()
```

### 2.3 DeckWord Through Model

```python
class DeckWord(models.Model):
    """
    Many-to-many relationship between decks and words.
    Stores deck-specific settings for each word.
    """
    
    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        related_name='deck_words'
    )
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name='deck_assignments'
    )
    
    # Word-specific settings in this deck
    show_romaji = models.BooleanField(default=True)
    show_kanji = models.BooleanField(default=True)
    position = models.PositiveIntegerField(
        default=0,
        help_text="Order of word in deck"
    )
    
    # Mastery tracking
    mastery_level = models.PositiveIntegerField(
        default=0,
        help_text="0 = not learned, higher = more learned"
    )
    last_reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    class Meta:
        unique_together = ['deck', 'word']
        ordering = ['position']
        indexes = [
            models.Index(fields=['deck', 'position']),
        ]
    
    def __str__(self):
        return f"{self.deck.name} - {self.word}"
```

### 2.4 List Model

```python
class List(Collection):
    """
    A simple list of words or sentences.
    Less structured than a deck, used for quick reference.
    """
    
    # List-specific items
    words = models.ManyToManyField(
        Word,
        related_name='lists',
        blank=True,
        through='ListWord'
    )
    
    sentences = models.ManyToManyField(
        Sentence,
        related_name='lists',
        blank=True,
        through='ListSentence'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Lists"
        indexes = [
            models.Index(fields=['owner']),
        ]
    
    def __str__(self):
        return f"List '{self.name}'"
```

### 2.5 ListWord Through Model

```python
class ListWord(models.Model):
    """
    Many-to-many relationship between lists and words.
    Minimal settings for simple lists.
    """
    
    list = models.ForeignKey(
        List,
        on_delete=models.CASCADE,
        related_name='list_words'
    )
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name='list_assignments'
    )
    
    position = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['list', 'word']
        ordering = ['position']
        indexes = [
            models.Index(fields=['list', 'position']),
        ]
    
    def __str__(self):
        return f"{self.list.name} - {self.word}"
```

## 3. Learning Progress Model

### 3.1 UserProgress Model

```python
class UserProgress(models.Model):
    """
    Tracks overall learning progress for a user.
    Aggregates progress from all collections.
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress'
    )
    
    # Overall statistics
    total_words_mastered = models.PositiveIntegerField(default=0)
    total_sentences_mastered = models.PositiveIntegerField(default=0)
    total_review_count = models.PositiveIntegerField(default=0)
    total_study_time_minutes = models.PositiveIntegerField(default=0)
    
    # Average scores
    average_quiz_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    # Last activity
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    last_decks_reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['last_reviewed_at']),
        ]
    
    def __str__(self):
        return f"Progress for {self.user.username}"
    
    @property
    def mastery_percentage(self):
        total = self.user.created_words.count() + self.user.created_sentences.count()
        if total == 0:
            return 0.0
        mastered = (
            self.total_words_mastered + 
            self.total_sentences_mastered
        )
        return (mastered / total) * 100
```

### 3.2 DeckProgress Model

```python
class DeckProgress(models.Model):
    """
    Tracks progress on individual decks.
    """
    
    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        related_name='progress'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deck_progress'
    )
    
    # Completion tracking
    items_reviewed = models.PositiveIntegerField(default=0)
    items_mastered = models.PositiveIntegerField(default=0)
    completion_percentage = models.PositiveIntegerField(default=0)
    
    # Statistics
    total_attempts = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    average_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['deck', 'user']
        indexes = [
            models.Index(fields=['deck', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.deck.name}"
    
    @property
    def is_completed(self):
        return self.completion_percentage >= 100
    
    @property
    def accuracy(self):
        if self.total_attempts == 0:
            return 0.0
        return (self.correct_answers / self.total_attempts) * 100
```

### 3.3 WordProgress Model

```python
class WordProgress(models.Model):
    """
    Tracks progress on individual words.
    """
    
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name='progress'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='word_progress'
    )
    
    # Mastery tracking
    mastery_level = models.PositiveIntegerField(
        default=0,
        help_text="0 = new, 1-5 = learning, 6+ = mastered"
    )
    
    # Review tracking
    review_count = models.PositiveIntegerField(default=0)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    next_review_at = models.DateTimeField(null=True, blank=True)
    
    # Performance metrics
    total_attempts = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    average_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['word', 'user']
        indexes = [
            models.Index(fields=['word', 'user']),
            models.Index(fields=['next_review_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.word} (mastery: {self.mastery_level})"
    
    @property
    def is_mastered(self):
        return self.mastery_level >= 6
    
    @property
    def accuracy(self):
        if self.total_attempts == 0:
            return 0.0
        return (self.correct_answers / self.total_attempts) * 100
```

## 4. Dictionary Import Model

### 4.1 ImportJob Model

```python
class ImportJob(models.Model):
    """
    Tracks dictionary import jobs (CSV/JSON files).
    """
    
    JOB_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='import_jobs'
    )
    
    import_type = models.CharField(
        max_length=20,
        choices=[
            ('csv', 'CSV'),
            ('json', 'JSON'),
        ]
    )
    
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    
    # Import results
    total_items = models.PositiveIntegerField(default=0)
    successful_items = models.PositiveIntegerField(default=0)
    failed_items = models.PositiveIntegerField(default=0)
    
    status = models.CharField(
        max_length=20,
        choices=JOB_STATUS_CHOICES,
        default='pending'
    )
    
    # Error tracking
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.file_name} ({self.status})"
    
    @property
    def success_rate(self):
        if self.total_items == 0:
            return 0.0
        return (self.successful_items / self.total_items) * 100
```

### 4.2 ImportItem Model

```python
class ImportItem(models.Model):
    """
    Individual item from an import job.
    Tracks success/failure of each item.
    """
    
    job = models.ForeignKey(
        ImportJob,
        on_delete=models.CASCADE,
        related_name='import_items'
    )
    
    item_type = models.CharField(
        max_length=20,
        choices=[
            ('word', 'Word'),
            ('sentence', 'Sentence'),
        ]
    )
    
    row_number = models.PositiveIntegerField()
    
    # Data from import
    raw_data = models.JSONField()
    
    # Processing results
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('duplicate', 'Duplicate'),
            ('invalid', 'Invalid'),
            ('error', 'Error'),
        ]
    )
    
    # Error details
    error_message = models.TextField(blank=True)
    
    # Created/updated entities
    created_entities = models.JSONField(
        default=list,
        blank=True,
        help_text="List of created entity IDs"
    )
    updated_entities = models.JSONField(
        default=list,
        blank=True,
        help_text="List of updated entity IDs"
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['job', 'status']),
        ]
    
    def __str__(self):
        return f"Row {self.row_number} - {self.item_type} ({self.status})"
```

## 5. Notes and Annotations Model

### 5.1 UserNote Model

```python
class UserNote(models.Model):
    """
    User-created notes and annotations.
    Can be attached to words, sentences, or decks.
    """
    
    note_type = models.CharField(
        max_length=20,
        choices=[
            ('word_note', 'Word Note'),
            ('sentence_note', 'Sentence Note'),
            ('deck_note', 'Deck Note'),
            ('general', 'General'),
        ]
    )
    
    # Target entity
    target_type = models.CharField(
        max_length=50,
        choices=[
            ('word', 'Word'),
            ('sentence', 'Sentence'),
            ('deck', 'Deck'),
        ]
    )
    target_id = models.PositiveIntegerField()
    
    # Content
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    
    # Metadata
    is_public = models.BooleanField(
        default=False,
        help_text="Visible to other users who have access to the target"
    )
    
    # User association
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'target_type', 'target_id']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        target = self.get_target_object()
        return f"Note by {self.user.username} on {target}"
    
    def get_target_object(self):
        """Get the target entity object."""
        if self.target_type == 'word':
            return get_object_or_404(Word, id=self.target_id)
        elif self.target_type == 'sentence':
            return get_object_or_404(Sentence, id=self.target_id)
        elif self.target_type == 'deck':
            return get_object_or_404(Deck, id=self.target_id)
        return None
```

## 6. Data Relationships Diagram

```
┌─────────────┐       ┌─────────────┐
│    User     │       │   Language  │
└──────┬──────┘       └──────┬──────┘
       │                     │
       │ ───────────────────►│ (1:1 via target_language)
       │                     │
       │                     ▼
       │              ┌──────────────┐
       │              │   Word       │
       │              └──────┬───────┘
       │                     │
       │                     │ ◄───────┐
       │                     │          │
       │                     │          │
       ▼                     │          │
┌─────────────┐      ┌──────────────┐   │
│    Deck     │      │ DeckWord     │   │
└──────┬──────┘      └──────┬───────┘   │
       │                    │            │
       │ ◄──────────────────┘            │
       │                                 │
       │                                 ▼
       │                          ┌──────────────┐
       │                          │    Sentence  │
       │                          └──────┬───────┘
       │                                 │
       └─────────────────────────────────┘
                                       │
                                       │
                                        ▼
                               ┌───────────────┐
                               │   UserProgress│
                               └──────┬────────┘
                                      │
                                      ▼
                               ┌───────────────┐
                               │  DeckProgress  │
                               │ WordProgress  │
                               └───────────────┘

User Note
    │
    ├──► Word Note
    ├──► Sentence Note
    └──► Deck Note
```

## 7. Indexing Strategy

### 7.1 Primary Indexes

| Table | Field(s) | Purpose |
|-------|----------|---------|
| `word` | `kanji` | Kanji-based lookups |
| `word` | `romaji` | Romaji-based lookups |
| `word` | `tags` | Tag filtering |
| `sentence` | `created_at` | Chronological queries |
| `deck` | `owner` | User's decks |
| `deckword` | `deck`, `position` | Ordered deck items |
| `listword` | `list`, `position` | Ordered list items |
| `userprogress` | `last_reviewed_at` | Activity tracking |
| `deckprogress` | `deck`, `user` | User-deck progress |
| `wordprogress` | `word`, `user` | User-word progress |
| `wordprogress` | `next_review_at` | Spaced repetition |
| `importjob` | `user`, `status` | Job filtering |

### 7.2 Composite Indexes

- `deckword` - `(deck, word)` for unique constraint
- `listword` - `(list, word)` for unique constraint
- `wordprogress` - `(word, user)` for unique constraint
- `deckprogress` - `(deck, user)` for unique constraint

## 8. Normalization Strategy

The model uses a normalized design:

1. **Words and Sentences are shared** - Not duplicated per user
2. **Progress is denormalized** - Stored separately per user for fast access
3. **Collections are user-owned** - Decks and lists are user-specific
4. **Many-to-many through tables** - Allow per-item settings

### Justification

- **Normalization** reduces data duplication and ensures consistency
- **Denormalized progress** enables fast read operations
- **Through tables** provide flexibility for deck-specific settings
- **Shared vocabulary** enables collaborative learning (users can access same words)

## 9. Data Constraints

### 9.1 Unique Constraints

- `Language.code` - ISO code uniqueness
- `DeckWord` - `(deck, word)` composite key
- `ListWord` - `(list, word)` composite key
- `WordProgress` - `(word, user)` composite key
- `DeckProgress` - `(deck, user)` composite key

### 9.2 Validation Rules

- **Kanji**: Max 100 characters, optional
- **Kana**: Max 50 characters, required
- **Romaji**: Max 50 characters, optional
- **Meaning**: Max 1000 characters (TextField)
- **Sentence text**: Max 1000 characters
- **Deck name**: Max 200 characters
- **List name**: Max 200 characters

### 9.3 Soft Deletes

Current design uses hard deletes. Consider implementing soft deletes for:

- User-created content (for recovery)
- Import jobs (for audit trails)
- Notes (for versioning)

Implementation would require `deleted_at` field and queryset filtering.

## 10. Future Extensions

### 10.1 Multi-Language Support

Current design supports one target language per user. Future extensions:

- Add `learning_language` to `User` (default target)
- Create `Word` entries per language
- Support polyglot learning (e.g., Russian → Japanese → English)

### 10.2 Spaced Repetition

Add SRS (SuperMemo-2 algorithm) fields:

- `ease_factor` - Spacing multiplier
- `interval` - Days until next review
- `repetition` - Current repetition count

### 10.3 Social Features

Add fields for:

- `favorite_words` - User favorites across decks
- `shared_collections` - Collections shared with groups
- `collaborative_decks` - Multi-user decks

### 10.4 Gamification

Add fields for:

- `streak_days` - Consecutive days studying
- `study_sessions` - Total study sessions
- `achievements` - JSONField of unlocked achievements
