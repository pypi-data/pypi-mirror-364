/**
 * Constants and loading methods for chat context menu
 */
import { Contents, KernelMessage } from '@jupyterlab/services';
import { ToolService } from '../../Services/ToolService';

export interface MentionContext {
  type: 'rules' | 'data' | 'variable' | 'cell';
  id: string;
  name: string;
  content?: string;
  description?: string;
}

// Constants
export const VARIABLE_TYPE_BLACKLIST = [
  'module',
  'type',
  'function',
  'ZMQExitAutocall',
  'method'
];

export const VARIABLE_NAME_BLACKLIST = ['In', 'Out'];

export const MENTION_CATEGORIES = [
  {
    id: 'rules',
    name: 'Rules',
    icon: '📄',
    description: 'Reusable prompt templates'
  },
  {
    id: 'data',
    name: 'Data',
    icon: '📊',
    description: 'Dataset references and info'
  },
  {
    id: 'variables',
    name: 'Variables',
    icon: '🔤',
    description: 'Code variables and values'
  },
  {
    id: 'cells',
    name: 'Cells',
    icon: '📝',
    description: 'Notebook cell references'
  }
];

/**
 * Class responsible for loading different types of context items
 */
export class ChatContextLoaders {
  private contentManager: Contents.IManager;
  private toolService: ToolService;

  constructor(contentManager: Contents.IManager, toolService: ToolService) {
    this.contentManager = contentManager;
    this.toolService = toolService;
  }

  /**
   * Initialize context items for each category
   */
  public async initializeContextItems(): Promise<
    Map<string, MentionContext[]>
  > {
    const contextItems = new Map<string, MentionContext[]>();

    // Initialize empty maps for each category
    contextItems.set('rules', []);
    contextItems.set('data', [
      {
        type: 'data',
        id: 'demo-dataset',
        name: 'demo-dataset',
        description: 'Sample dataset for demonstration',
        content: 'This is a demo dataset context'
      }
    ]);
    contextItems.set('variables', [
      {
        type: 'variable',
        id: 'demo-var',
        name: 'demo_variable',
        description: 'Sample variable for demonstration',
        content: 'x = 42  # Demo variable'
      }
    ]);
    contextItems.set('cells', [
      {
        type: 'cell',
        id: 'demo-cell',
        name: 'Cell 1',
        description: 'Sample cell for demonstration',
        content: 'print("Hello from demo cell")'
      }
    ]);

    console.log(
      'All context items after initialization:',
      Array.from(contextItems.entries())
    ); // Debug log

    return contextItems;
  }

  /**
   * Load datasets from the data directory
   */
  public async loadDatasets(): Promise<MentionContext[]> {
    try {
      const datasets = await this.contentManager.get('./data');
      console.log('Loaded datasets:', datasets); // Debug log

      if (datasets.content && Array.isArray(datasets.content)) {
        const datasetContexts: MentionContext[] = await Promise.all(
          datasets.content
            .filter(file => file.type === 'file')
            .map(async file => {
              // remove everything from the last dot to the end (e.g. ".json", ".csv", ".txt", etc.)
              const name = file.name.replace(/\.[^/.]+$/, '');

              const content = await this.contentManager.get(
                './data/' + file.name
              );

              const contentString = `${content.content}`;

              return {
                type: 'data' as const,
                id: file.path,
                name,
                description: 'Dataset file',
                content: contentString.slice(0, 1000)
              };
            })
        );

        return datasetContexts;
      }
    } catch (error) {
      console.error('Error loading datasets:', error);
    }

    return [];
  }

  /**
   * Load notebook cells
   */
  public async loadCells(): Promise<MentionContext[]> {
    console.log('Loading cells... ======================');
    const notebook = this.toolService.getCurrentNotebook();
    if (!notebook) {
      console.warn('No notebook available');
      return [];
    }

    const cellContexts: MentionContext[] = [];
    const cells = notebook.widget.model.cells as any;

    for (const cell of cells) {
      console.log('Cell:', cell); // Debug log
      console.log('Cell metadata:', cell.metadata); // Debug log

      const tracker = cell.metadata.cell_tracker;
      if (tracker) {
        cellContexts.push({
          type: 'cell',
          id: tracker.trackingId,
          name: tracker.trackingId,
          description: '',
          content: cell.sharedModel.getSource()
        });
      }
    }

    console.log('CELL LOADING, cells:', cells); // Debug log
    return cellContexts;
  }

  /**
   * Load variables from the current kernel
   */
  public async loadVariables(): Promise<MentionContext[]> {
    console.log('Loading variables... ======================');
    const kernel = this.toolService.getCurrentNotebook()?.kernel;
    if (!kernel) {
      console.warn('No kernel available');
      return [];
    }

    return new Promise(resolve => {
      // This Python snippet builds a dict of { varName: { type: ..., value: ... } }
      // and prints it as one JSON string.
      const code = `
        import json
        
        def to_jsonable(v):
            # Primitive types → leave as-is
            if isinstance(v, (int, float, str, bool, type(None))):
                return v
            # Lists/tuples → recursively convert
            if isinstance(v, (list, tuple)):
                return [to_jsonable(x) for x in v]
            # Dicts → recursively convert
            if isinstance(v, dict):
                return {k: to_jsonable(val) for k, val in v.items()}
            # Fallback → string repr
            return repr(v)
        
        data = {
            name: {
                "type": type(val).__name__,
                "value": to_jsonable(val)
            }
            for name, val in globals().items()
            if not name.startswith('_')
        }
        
        # Print as a single JSON blob
        print(json.dumps(data))
        `;

      // Buffer to accumulate the printed JSON
      let buffer = '';

      // Send execute request
      const future = kernel.requestExecute({ code });

      future.onIOPub = (msg: KernelMessage.IIOPubMessage) => {
        const msgType = msg.header.msg_type;
        if (msgType === 'stream') {
          // stdout comes in as a stream msg
          const text = (msg as KernelMessage.IStreamMsg).content.text;
          buffer += text;
        } else if (msgType === 'error') {
          // handle any Python exceptions
          const err = (msg as KernelMessage.IErrorMsg).content;
          console.error('Error fetching variables:', err.ename, err.evalue);
        }
      };

      future.done.then(() => {
        // Once execution is finished, try to parse the accumulated buffer
        try {
          const varsWithTypes = JSON.parse(buffer);
          console.log('Variables with types and values:', varsWithTypes);
          const variableContexts: MentionContext[] = [];
          for (const varName of Object.keys(varsWithTypes)) {
            if (VARIABLE_NAME_BLACKLIST.includes(varName)) continue;
            if (VARIABLE_TYPE_BLACKLIST.includes(varsWithTypes[varName].type))
              continue;

            variableContexts.push({
              type: 'variable',
              id: varName,
              name: varName,
              description: varsWithTypes[varName].type,
              content: varsWithTypes[varName].value
            });
          }
          resolve(variableContexts);
        } catch (e) {
          console.error('Failed to parse JSON output:', buffer, e);
          resolve([]);
        }
      });
    });
  }

  /**
   * Load template files from the templates directory
   */
  public async loadTemplateFiles(): Promise<MentionContext[]> {
    try {
      const files = await this.contentManager.get('./templates');

      if (files.content && Array.isArray(files.content)) {
        const templateContexts: MentionContext[] = files.content
          .filter(
            file => file.type === 'file' && file.name !== 'rule.example.md'
          )
          .map(file => {
            const displayName = file.name
              .replace(/^rule\./, '')
              .replace(/\.md$/, '');

            return {
              type: 'rules' as const,
              id: file.path,
              name: displayName,
              description: 'Rule file'
            };
          });

        return templateContexts;
      }
    } catch (error) {
      console.error('Error loading template files:', error);
    }

    return [];
  }

  /**
   * Load the content of a template file
   */
  public async loadTemplateContent(filePath: string): Promise<string> {
    try {
      const file = await this.contentManager.get(filePath, { content: true });
      if (file.content) {
        return typeof file.content === 'string'
          ? file.content
          : JSON.stringify(file.content);
      }
      return '';
    } catch (error) {
      console.error(`Error loading template file ${filePath}:`, error);
      return '';
    }
  }
}
