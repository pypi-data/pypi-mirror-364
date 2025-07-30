import { Cell } from '@jupyterlab/cells';
import { CodeMirrorEditor } from '@jupyterlab/codemirror';
import { EditorView, ViewPlugin } from '@codemirror/view';
import { MergeView, unifiedMergeView } from '@codemirror/merge';
import {
  Extension,
  StateEffect,
  StateField,
  Transaction,
  Compartment
} from '@codemirror/state';

/**
 * Callback interface for merge operations
 */
export interface MergeCallbacks {
  onAccept?: (cellId: string, newContent: string) => void;
  onReject?: (cellId: string, originalContent: string) => void;
}

/**
 * Interface for merge view state information
 */
export interface MergeViewState {
  cellId: string;
  cell: Cell;
  view: CodeMirrorEditor;
}

/**
 * PARTIAL MIGRATION: NotebookDiffTools.generateHtmlDiff → InlineDiffService
 *
 * This service provides a modern, CodeMirror-based inline diff experience
 * that replaces the previous HTML overlay approach using diff2html.
 *
 * Currently integrated in:
 * - ContextCellHighlighter.showDiffView() (✅ migrated for inline editing workflow)
 *
 * Original NotebookDiffTools workflow preserved for:
 * - NotebookDiffTools.display_diff() (uses original HTML overlays)
 * - DiffApprovalDialog (uses original generateHtmlDiff implementation)
 * - Diff manager workflows (continues to use existing approach)
 *
 * Migration Benefits (for migrated components):
 * - Better UX with CodeMirror's unified merge view (similar to Cursor)
 * - Native editor integration instead of HTML overlays
 * - Built-in accept/reject functionality via CodeMirror's merge controls
 * - Automatic theme support through CodeMirror
 * - Better performance and user interaction
 *
 * Future migration opportunities:
 * - Complete NotebookDiffTools.display_diff() migration
 * - Integrate with diff approval workflows
 * - Enhanced merge conflict resolution
 */

/**
 * Service for managing inline diffs in notebook cells using CodeMirror's unified merge view
 * This provides a Cursor-like inline diff experience with proper diff highlighting
 */
export class InlineDiffService {
  private activeMergeViews: Map<string, MergeViewState> = new Map();
  private mergeCallbacks: Map<string, MergeCallbacks> = new Map();
  private mergeCompartments: Map<string, Compartment> = new Map();

  /**
   * Show inline diff for a cell using CodeMirror's unified merge view
   * @param cell The notebook cell
   * @param originalContent The original content to compare against
   * @param newContent The new/proposed content
   * @param callbacks Optional callbacks for merge operations
   *
   * Note: CodeMirror's merge view provides built-in accept/reject controls,
   * so no custom controls are added. Callbacks are used for programmatic interactions.
   */
  public showInlineDiff(
    cell: Cell,
    originalContent: string,
    newContent: string,
    callbacks?: MergeCallbacks
  ): void {
    const cellId = cell.model.id;
    console.log(
      `[InlineDiffService] Showing unified merge view for cell ${cellId}`
    );

    // Store callbacks
    if (callbacks) {
      this.mergeCallbacks.set(cellId, callbacks);
    }

    // Get the CodeMirror editor instance
    const editor = cell.editor;
    if (!editor || !(editor instanceof CodeMirrorEditor)) {
      console.error('Cell editor is not a CodeMirrorEditor instance');
      return;
    }

    // Store diff state with callbacks
    this.activeMergeViews.set(cellId, {
      cellId,
      cell,
      view: editor
    });

    // Create the unified merge view
    this.createUnifiedMergeView(cell, originalContent, newContent);
  }

  /**
   * Create and configure the unified merge view
   */
  private createUnifiedMergeView(
    cell: Cell,
    originalContent: string,
    newContent: string
  ): void {
    const cellNode = cell.node;
    const editor = cell.editor as CodeMirrorEditor;
    const cellId = cell.model.id;

    // Add a class to indicate diff mode
    cellNode.classList.add('sage-ai-unified-diff-active');

    try {
      // Get the current editor view
      const currentView = editor.editor;

      // Set the new content first
      cell.model.sharedModel.setSource(newContent);

      // Create a state field to track merge operations
      const mergeTracker = StateField.define({
        create: () => ({ lastContent: newContent }),
        update: (value, transaction) => {
          // Check if this is a merge-related transaction
          if (transaction.docChanged) {
            const newContent = transaction.newDoc.toString();

            // Check if content changed due to merge operations
            if (newContent !== value.lastContent) {
              // Determine if this was an accept (content matches new) or reject (content matches original)
              const callbacks = this.mergeCallbacks.get(cellId);
              if (callbacks) {
                if (newContent === originalContent) {
                  // Content reverted to original - this was a reject
                  setTimeout(
                    () => callbacks.onReject?.(cellId, originalContent),
                    0
                  );
                } else if (newContent !== originalContent) {
                  // Content is different from original - this could be an accept or manual edit
                  setTimeout(() => callbacks.onAccept?.(cellId, newContent), 0);
                }
              }

              // Check if merge view should be cleaned up after changes
              setTimeout(() => {
                this.cleanupMergeViewIfEmpty(cell);
              }, 150); // Allow time for DOM updates
            }

            return { lastContent: newContent };
          }
          return value;
        }
      });

      // Create unified merge view extension
      const mergeExtension = unifiedMergeView({
        original: originalContent,
        gutter: false,
        mergeControls: true,
        highlightChanges: true,
        syntaxHighlightDeletions: true,
        allowInlineDiffs: true
      });

      // Create the monitoring plugin for this specific cell
      const monitorPlugin = this.createMergeViewMonitor(cell);

      // Apply the merge view extension with change tracking and monitoring
      this.extendEditorExtensions(
        currentView,
        [mergeExtension, mergeTracker, monitorPlugin],
        cellId
      );
    } catch (error) {
      console.error('Error creating unified merge view:', error);
    }
  }

  /**
   * Reconfigure the editor to include the merge view extension using a compartment
   */
  private extendEditorExtensions(
    currentView: EditorView,
    extensions: Extension[],
    cellId: string
  ): void {
    // Create a compartment for this merge view so it can be easily removed
    const compartment = new Compartment();
    this.mergeCompartments.set(cellId, compartment);

    // Use the compartment to add the merge view extensions
    currentView.dispatch({
      effects: StateEffect.appendConfig.of(compartment.of(extensions))
    });

    console.log(
      '[InlineDiffService] Configured unified merge view with change tracking'
    );
  }

  /**
   * Check if there are any remaining merge chunks in the DOM
   */
  private hasRemainingMergeChunks(viewNode: HTMLElement): boolean {
    // Check for merge chunks in the DOM
    const deletedChunks = viewNode.querySelectorAll('.cm-deletedChunk');
    const changedLines = viewNode.querySelectorAll('.cm-changedLine');

    return deletedChunks.length > 0 || changedLines.length > 0;
  }

  /**
   * Remove merge extensions from a cell's editor view
   */
  public removeMergeExtensions(cell: Cell): void {
    const cellId = cell.model.id;
    const compartment = this.mergeCompartments.get(cellId);

    if (compartment && cell.editor instanceof CodeMirrorEditor) {
      const currentView = cell.editor.editor;

      // Remove the merge extensions by reconfiguring the compartment to empty
      currentView.dispatch({
        effects: compartment.reconfigure([])
      });

      // Clean up stored references
      this.mergeCompartments.delete(cellId);
      this.mergeCallbacks.delete(cellId);
      this.activeMergeViews.delete(cellId);

      // Remove the diff mode class
      cell.node.classList.remove('sage-ai-unified-diff-active');

      console.log(
        `[InlineDiffService] Removed merge extensions for cell ${cellId}`
      );
    }
  }

  /**
   * Clean up merge view for a cell if no chunks remain
   */
  public cleanupMergeViewIfEmpty(cell: Cell): boolean {
    const cellId = cell.model.id;
    const mergeView = this.activeMergeViews.get(cellId);

    if (
      mergeView &&
      !this.hasRemainingMergeChunks(mergeView.view.editor.contentDOM!)
    ) {
      // No chunks remain, remove the merge extensions completely
      this.removeMergeExtensions(cell);
      return true;
    }

    return false;
  }

  /**
   * Monitor merge view and auto-cleanup when chunks are resolved
   */
  private createMergeViewMonitor(cell: Cell): ViewPlugin<any> {
    return ViewPlugin.define(() => ({
      update: () => {
        // Check if all chunks have been resolved after each update
        setTimeout(() => {
          this.cleanupMergeViewIfEmpty(cell);
        }, 100); // Small delay to let DOM updates complete
      }
    }));
  }
}

// Global singleton instance
export const inlineDiffService = new InlineDiffService();
