from django.contrib import admin
from .models import Category, Course, CoursePrice, CourseSection, Lesson

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class CourseSectionInline(admin.TabularInline):
    model = CourseSection
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'level', 'status', 'is_free', 'created_at')
    list_filter = ('status', 'level', 'is_free', 'organization')
    search_fields = ('title', 'slug', 'organization__name')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CourseSectionInline]

@admin.register(CoursePrice)
class CoursePriceAdmin(admin.ModelAdmin):
    list_display = ('course', 'amount_minor', 'currency', 'is_active')
    list_filter = ('currency', 'is_active')

@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'position')
    list_filter = ('course',)
    ordering = ('course', 'position')
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'lesson_type', 'position', 'duration_seconds', 'is_required')
    list_filter = ('lesson_type', 'is_required')
    search_fields = ('title', 'section__title', 'section__course__title')
