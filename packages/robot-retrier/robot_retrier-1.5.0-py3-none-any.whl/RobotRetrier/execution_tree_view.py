import tkinter as tk
from tkinter import ttk
from datetime import datetime

try:
    from robot.libraries.BuiltIn import BuiltIn
except ImportError:
    BuiltIn = None

class ExecutionTreeModel:
    """Data model for recording the Robot Framework execution tree."""
    def __init__(self):
        self.root = None
        self.current_stack = []
        self._step_counter = 1 # monotonically increasing index for steps

    def start_suite(self, data, result):
        now = datetime.now()
        node = {
            'type': 'SUITE',
            'name': getattr(data, 'name', ''),
            'status': None,
            'children': [],
            'attrs': {
                'source': getattr(data, 'source', ''),
            },
            'start_time': now,
            'end_time': None,
            'index': len(self.current_stack) == 0 and 1 or None,
            'msg': ''
        }
        if not self.root:
            self.root = node
            self.current_stack = [self.root]
        else:
            self.current_stack[-1]['children'].append(node)
            self.current_stack.append(node)

    def end_suite(self, data, result):
        now = datetime.now()
        if self.current_stack:
            node = self.current_stack[-1]
            node['status'] = getattr(result, 'status', None)
            node['end_time'] = now
            if hasattr(result, 'message'):
                node['msg'] = getattr(result, 'message')
            self.current_stack.pop()

    def start_test(self, data, result):
        now = datetime.now()
        node = {
            'type': 'TEST',
            'name': getattr(data, 'name', ''),
            'status': None,
            'children': [],
            'attrs': {
                'tags': getattr(data, 'tags', []),
            },
            'start_time': now,
            'end_time': None,
            'index': self._step_counter,  # test case also indexed
            'msg': ''
        }
        self._step_counter += 1
        if self.current_stack:
            self.current_stack[-1]['children'].append(node)
            self.current_stack.append(node)

    def end_test(self, data, result):
        now = datetime.now()
        if self.current_stack:
            node = self.current_stack[-1]
            node['status'] = getattr(result, 'status', None)
            node['end_time'] = now
            if hasattr(result, 'message'):
                node['msg'] = getattr(result, 'message')
            self.current_stack.pop()

    def start_keyword(self, data, result):
        now = datetime.now()
        kwname = getattr(data, 'kwname', None)
        name = kwname if kwname is not None else getattr(data, 'name', '')
        arglist = getattr(data, 'args', [])
        node = {
            'type': 'KEYWORD',
            'name': name,
            'status': None,
            'children': [],
            'attrs': {
                'args': arglist,
            },
            'start_time': now,
            'end_time': None,
            'index': self._step_counter,
            'msg': ''
        }
        self._step_counter += 1
        if self.current_stack:
            self.current_stack[-1]['children'].append(node)
            self.current_stack.append(node)

    def end_keyword(self, data, result):
        now = datetime.now()
        if self.current_stack:
            node = self.current_stack[-1]
            node['status'] = getattr(result, 'status', None)
            node['end_time'] = now
            if hasattr(result, 'message'):
                node['msg'] = getattr(result, 'message')
            self.current_stack.pop()

class ExecutionTreeView(ttk.Frame):
    STATUS_ICONS = {
        'PASS': '🟢',
        'FAIL': '🔴',
        'SKIP': '⚪',
        None:  ''
    }

    def __init__(self, master, tree_model):
        super().__init__(master)
        self.tree_model = tree_model

        # Columns: index, type, status, args, start, dur, msg (NO source)
        self.tree = ttk.Treeview(
            self,
            columns=('index', 'type', 'status', 'args', 'start', 'dur', 'msg'),
            selectmode="browse"
        )
        self.tree.heading('#0', text='Name')
        self.tree.heading('index', text='Step#')
        self.tree.heading('type', text='Type')
        self.tree.heading('status', text='Status')
        self.tree.heading('args', text='Arguments/Values')
        self.tree.heading('start', text='Start')
        self.tree.heading('dur', text='Duration (s)')
        self.tree.heading('msg', text='Message')
        self.tree.column('index', width=45, anchor='center')
        self.tree.column('type', width=60, anchor='center')
        self.tree.column('status', width=60, anchor='center')
        self.tree.column('args', width=190, anchor='w')
        self.tree.column('start', width=115, anchor='center')
        self.tree.column('dur', width=80, anchor='center')
        self.tree.column('msg', width=300, anchor='w')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ysb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        ysb.pack(side=tk.RIGHT, fill='y')
        self.tree.configure(yscroll=ysb.set)
        self.tree.bind("<Button-3>", self._on_right_click)
        self._copy_menu = tk.Menu(self.tree, tearoff=0)
        self._copy_menu.add_command(label="Copy Row", command=self._copy_selected_row)

        self.refresh_tree()

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())

        if self.tree_model.root:
            # always add and expand root (suite)
            root_id = self._add_node('', self.tree_model.root, 0, expand=True)

            # Expand last test under root
            tests = self.tree_model.root.get('children', [])
            if tests:
                last_test = tests[-1]
                test_id = self.tree.get_children(root_id)[-1]
                self.tree.item(test_id, open=True)

                # Expand/select last keyword under the test
                keywords = last_test.get('children', [])
                if keywords:
                    # Expand all keywords (so user can see the whole current test progress)
                    for idx in range(len(keywords)):
                        kw_id = self.tree.get_children(test_id)[idx]
                    # Select and scroll to last keyword
                    last_kw_id = self.tree.get_children(test_id)[-1]
                    self.tree.selection_set(last_kw_id)
                    self.tree.see(last_kw_id)
            else:
                # No tests - just expand root suite
                self.tree.item(root_id, open=True)

        self._apply_striping()

    def _apply_striping(self):
        for idx, item in enumerate(self.tree.get_children('')):
            self.tree.tag_configure(f'stripe{idx % 2}', background='#f7f7f7' if idx%2 else '#ffffff')
            self.tree.item(item, tags=self.tree.item(item, 'tags') + (f'stripe{idx % 2}',))
            self._stripe_children(item, idx % 2)

    def _stripe_children(self, parent, base_idx):
        for i, child in enumerate(self.tree.get_children(parent)):
            idx = (base_idx + i) % 2
            self.tree.tag_configure(f'stripe{idx}', background='#f7f7f7' if idx else '#ffffff')
            self.tree.item(child, tags=self.tree.item(child, 'tags') + (f'stripe{idx}',))
            self._stripe_children(child, idx)

    def _add_node(self, parent, node, row, expand=False):
        typ = node['type']
        name = node['name']
        status = node['status']
        icon = self.STATUS_ICONS.get(status, '')
        index = node.get('index', '')
        attrs = node.get('attrs', {})
        args = attrs.get('args', [])
        msg = node.get('msg', '') or ""
        st = node.get('start_time')
        et = node.get('end_time')
        start_str = st.strftime("%H:%M:%S") if st else ""
        duration = (et - st).total_seconds() if (st and et) else ""
        if duration != "":
            duration = f"{duration:.2f}"
        arg_strs = []
        for arg in args:
            val = arg
            if BuiltIn:
                try:
                    if isinstance(arg, str) and arg.startswith("${") and arg.endswith("}"):
                        v2 = BuiltIn().get_variable_value(arg)
                        if v2 is not None:
                            val = v2
                except Exception:
                    pass
            if str(val) != str(arg):
                arg_strs.append(f"{arg}={val!r}")
            else:
                arg_strs.append(str(arg))
        args_rendered = ', '.join(arg_strs)
        tags = [status.lower() if status else '', 'testbold' if typ == 'TEST' else 'reg']
        text = f"{icon} {name}"

        self.tree.tag_configure('pass', foreground='green')
        self.tree.tag_configure('fail', foreground='red')
        self.tree.tag_configure('skip', foreground='gray')
        self.tree.tag_configure('testbold', font=('Segoe UI', 10, 'bold'))
        self.tree.tag_configure('reg', font=('Segoe UI', 10, 'normal'))

        node_id = self.tree.insert(
            parent, 'end',
            text=text,
            values=(index, typ, status or '', args_rendered, start_str, duration, msg[:200]),
            tags=tags
        )

        # Expand current node if asked (used for suite root)
        if expand:
            self.tree.item(node_id, open=True)

        for idx, child in enumerate(node.get('children', [])):
            self._add_node(node_id, child, row + idx + 1)

        return node_id

    def _on_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self._copy_menu.post(event.x_root, event.y_root)

    def _copy_selected_row(self):
        selected = self.tree.selection()
        if not selected:
            return
        iid = selected[0]
        values = self.tree.item(iid)["values"]
        text = self.tree.item(iid)["text"]
        full_row = [str(text)] + [str(v) for v in values]
        self.clipboard_clear()
        self.clipboard_append('\t'.join(full_row))
