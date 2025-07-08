"""
Django admin configuration for the GCode API.

This module configures the Django admin interface for the gcode_api app.
Currently, the API doesn't have models that require admin management,
but this file can be extended to include admin configurations for
future models such as logging, user management, or caching.

The admin interface can be useful for:
- Monitoring API usage and performance
- Managing user access and permissions
- Viewing conversion and evaluation logs
- Managing cached files and cleanup
"""

from django.contrib import admin
from .models import User, SignatureData

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Admin interface for User model.
    """
    list_display = ('name', 'email', 'role', 'department', 'faculty', 'created_at', 'updated_at')
    list_filter = ('role', 'department', 'faculty', 'created_at')
    search_fields = ('name', 'email', 'department', 'faculty')
    readonly_fields = ('created_at', 'updated_at', 'submitted_at')
    ordering = ('-updated_at',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'role')
        }),
        ('Organizational Information', {
            'fields': ('department', 'faculty')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'submitted_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['export_as_csv']
    
    def export_as_csv(self, request, queryset):
        """Export selected users as CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Role', 'Department', 'Faculty', 'Created At'])
        
        for user in queryset:
            writer.writerow([
                user.name, user.email, user.role, 
                user.department, user.faculty, user.created_at
            ])
        
        return response
    
    export_as_csv.short_description = "Export selected users as CSV"

@admin.register(SignatureData)
class SignatureDataAdmin(admin.ModelAdmin):
    """
    Admin interface for SignatureData model.
    """
    list_display = ('user', 'created_at', 'svg_preview', 'gcode_preview')
    list_filter = ('created_at', 'user__role')
    search_fields = ('user__name', 'user__email')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def svg_preview(self, obj):
        """Show truncated SVG data."""
        return f"{obj.svg_data[:50]}..." if len(obj.svg_data) > 50 else obj.svg_data
    svg_preview.short_description = 'SVG Preview'
    
    def gcode_preview(self, obj):
        """Show truncated G-code data."""
        return f"{obj.gcode_data[:50]}..." if len(obj.gcode_data) > 50 else obj.gcode_data
    gcode_preview.short_description = 'G-code Preview'
    
    fieldsets = (
        ('Data', {
            'fields': ('user', 'svg_data', 'gcode_data')
        }),
        ('Metadata', {
            'fields': ('gcode_metadata',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )