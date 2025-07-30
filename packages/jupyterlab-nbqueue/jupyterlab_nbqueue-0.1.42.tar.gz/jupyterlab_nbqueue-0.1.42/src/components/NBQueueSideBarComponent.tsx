/**
 * NBQueue Sidebar Component
 * 
 * React component that provides a sidebar interface for managing and monitoring
 * workflow jobs in the NBQueue system. Displays job status, logs, and provides
 * controls for job management (refresh, view logs, delete, download).
 */

import { AppBar, Avatar, Container, CssBaseline, Dialog, DialogContent, DialogContentText, DialogProps, DialogTitle, Grid, IconButton, List, ListItem, ListItemAvatar, ListItemSecondaryAction, ListItemText, Slide, Toolbar, Typography } from '@mui/material'
import Refresh from '@mui/icons-material/Refresh';
import Done from '@mui/icons-material/Done';
import Error from '@mui/icons-material/Error';
import Pending from '@mui/icons-material/Pending';
import Visibility from '@mui/icons-material/Visibility';
import Delete from '@mui/icons-material/Delete';
import Close from '@mui/icons-material/Close';
import FileDownloadOutlined from '@mui/icons-material/FileDownloadOutlined';

import React from 'react'
import { requestAPI } from '../handler';
import { 
     WorkflowsResponse
} from '../common/types';
import { TransitionProps } from '@mui/material/transitions';

/** Interface for workflow data structure */
interface Workflow {
     name: string,
     status: string,
}

/** Transition component for dialog animations */
const Transition = React.forwardRef(function Transition(
     props: TransitionProps & {
          children: React.ReactElement;
     },
     ref: React.Ref<unknown>,
) {
     return <Slide direction="up" ref={ref} {...props} />;
});

/** Props interface for the NBQueueSideBarComponent */
interface NBQueueSideBarComponentProps {
     bucket: string;
}

/**
 * Main sidebar component for workflow management
 * 
 * Provides a comprehensive interface for viewing, managing, and monitoring
 * NBQueue workflows including status indicators and job controls.
 */
const NBQueueSideBarComponent: React.FC<NBQueueSideBarComponentProps> = (props): JSX.Element => {
     // Component state management
     const [bucket] = React.useState(props.bucket);
     const [dense] = React.useState(true)
     const [workflows, setWorkflows] = React.useState<Workflow[]>([])
     const [workflowName, setWorkflowName] = React.useState('');
     const [scroll, setScroll] = React.useState<DialogProps['scroll']>('paper');
     const [open, setOpen] = React.useState(false);
     const [contentLog, setContentLog] = React.useState('');

     /**
      * Renders appropriate status icon based on workflow status
      * @param status - Current workflow status
      * @returns JSX element with appropriate status icon
      */
     function AvatarStatusIcon({ status }: { status: string }) {
          console.log(status);

          switch (status) {
               case 'Succeeded':
                    return (<Done />)
                    break;

               case 'Running':
                    return (<Pending />)
                    break;

               case 'Failed':
                    return (<Error />)
                    break;

               default:
                    break;
          }
     }

     /**
      * Fetches the list of workflows from the API
      * Updates the component state with the retrieved workflows
      */
     const getWorkflows = async () => {
          const wf = await requestAPI<WorkflowsResponse>('workflows?bucket=' + bucket, {
               method: 'GET'
          })

          console.log(wf)
          setWorkflows(wf)
     };

     /**
      * Retrieves logs for a specific workflow
      * @param workflowName - Name of the workflow to get logs for
      * @param bucket - Bucket identifier
      * @returns Promise resolving to workflow logs
      */
     const getWorkflowLog = async (workflowName: string, bucket: string) => {
          const logs = await requestAPI<string>('workflow?workflow_name=' + workflowName + '&bucket=' + bucket, {
               method: 'GET'
          })
          console.log(logs)
          return logs
     };

     /**
      * Deletes a specific workflow
      * @param workflowName - Name of the workflow to delete
      * @param bucket - Bucket identifier  
      * @returns Promise resolving to deletion result
      */
     const deleteWorkflowLog = async (workflowName: string, bucket: string) => {
          const logs = await requestAPI<{success: boolean; message?: string}>('workflow?workflow_name=' + workflowName + '&bucket=' + bucket, {
               method: 'DELETE'
          })
          console.log(logs)
          return logs
     };

     /**
      * Downloads workflow logs
      * @param workflowName - Name of the workflow to download logs for
      * @param bucket - Bucket identifier
      * @returns Promise resolving to download data
      */
     const downloadWorkflowLog = async (workflowName: string, bucket: string) => {
          const logs = await requestAPI<Blob | string>('workflow/download?workflow_name=' + workflowName + '&bucket=' + bucket, {
               method: 'GET'
          })
          console.log(logs)
          return logs
     };

     /**
      * Handles refresh button click to reload workflows
      */
     const handleRefreshClick = (event: React.MouseEvent<HTMLButtonElement>) => {
          getWorkflows()
     };

     /**
      * Handles log view button click
      * Opens dialog with workflow logs
      * @param scrollType - Dialog scroll behavior
      * @param workflowName - Name of workflow to view logs for
      * @param bucket - Bucket identifier
      */
     const handleLogClick = (scrollType: DialogProps['scroll'], workflowName: string, bucket: string) => async () => {
          try {
               const logs = await getWorkflowLog(workflowName, bucket)

               console.log(`Endpoint Workflow log Result => ${logs}`)
               setContentLog(logs)
               setWorkflowName(workflowName)

          } catch (error) {
               console.log(`Error => ${JSON.stringify(error, null, 2)}`)
          }

          console.log(`Workflow Name => ${workflowName}`)
          setOpen(true);
          setScroll(scrollType);
     };

     /**
      * Handles download button click for workflow logs
      * @param scrollType - Dialog scroll behavior
      * @param workflowName - Name of workflow to download
      * @param bucket - Bucket identifier
      */
     const handleDownloadClick = (scrollType: DialogProps['scroll'], workflowName: string, bucket: string) => async () => {
          try {
               console.log('handleDownloadClick');
               const logs = await downloadWorkflowLog(workflowName, bucket)
               console.log(`Endpoint Workflow log Result => ${logs}`)

          } catch (error) {
               console.log(`Error => ${JSON.stringify(error, null, 2)}`)
          }

          console.log(`Workflow Name => ${workflowName}`)
     };

     const handleDeleteClick = (scrollType: DialogProps['scroll'], workflowName: string, bucket: string) => async () => {
          try {
               console.log('handleDeleteClick');

               const logs = await deleteWorkflowLog(workflowName, bucket)
               console.log(`Endpoint Workflow log Result => ${logs}`)
          } catch (error) {
               console.log(`Error => ${JSON.stringify(error, null, 2)}`)
          }

          console.log(`Workflow Name => ${workflowName}`)
          getWorkflows()
     };

     const handleClose = () => {
          setOpen(false);
     };

     const descriptionElementRef = React.useRef<HTMLElement>(null);
     React.useEffect(() => {
          if (open) {
               const { current: descriptionElement } = descriptionElementRef;
               if (descriptionElement !== null) {
                    descriptionElement.focus();
               }
          }
     }, [open]);

     React.useEffect(() => {
          getWorkflows()
          console.log(workflows);
     }, [])

     return (
          <React.Fragment>
               <AppBar>
                    <Toolbar>
                         <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                              NBQueue job list
                         </Typography>
                         <IconButton aria-label="delete" onClick={handleRefreshClick} color="inherit">
                              <Refresh />
                         </IconButton>
                    </Toolbar>
               </AppBar>
               <Toolbar />
               <Container sx={{
                    height: '100%', // Limits height to enable scrolling
                    overflowY: 'auto', // Enables vertical scroll when content exceeds height
                    paddingBottom: 5
               }}>

                    <Grid container direction="row" justifyContent="space-between" alignItems="flex-start" rowSpacing={1} columnSpacing={{ xs: 1, sm: 2, md: 3 }}>
                         <Grid item xs={12}>
                              <nav aria-label="execution job list">
                                   <List dense={dense}>
                                        {workflows.map(workflow => {
                                             return (<ListItem>
                                                  <ListItemAvatar>
                                                       <Avatar color={workflow.status}>
                                                            <AvatarStatusIcon status={workflow.status} />
                                                       </Avatar>
                                                  </ListItemAvatar>
                                                  <ListItemText
                                                       primary={workflow.name.split('/')[2]}
                                                       secondary={
                                                            <React.Fragment>
                                                                 <Typography
                                                                      sx={{ display: 'inline' }}
                                                                      component="span"
                                                                      variant="body2"
                                                                      color="text.primary"
                                                                 >
                                                                      {workflow.name.split('/')[3]}
                                                                 </Typography>
                                                                 {"—" + workflow.status}
                                                            </React.Fragment>
                                                       }
                                                  />
                                                  <ListItemSecondaryAction>
                                                       <IconButton edge="end" aria-label="view logs" id={workflow.name} itemID={workflow.name} onClick={handleLogClick('paper', workflow.name, bucket)}>
                                                            <Visibility />
                                                       </IconButton>

                                                       <IconButton edge="end" aria-label="view logs" id={workflow.name} itemID={workflow.name} onClick={handleDownloadClick('paper', workflow.name, bucket)}>
                                                            <FileDownloadOutlined />
                                                       </IconButton>
                                                       <IconButton edge="end" aria-label="view logs" id={workflow.name} itemID={workflow.name} onClick={handleDeleteClick('paper', workflow.name, bucket)}>
                                                            <Delete />
                                                       </IconButton>
                                                  </ListItemSecondaryAction>
                                             </ListItem>)
                                        }
                                        )}
                                        <ListItem>
                                             <ListItemText></ListItemText>
                                        </ListItem>
                                   </List>
                              </nav>
                         </Grid>
                    </Grid>
               </Container>
               <Dialog
                    fullScreen
                    open={open}
                    onClose={handleClose}
                    TransitionComponent={Transition}
               >
                    <AppBar sx={{ position: 'relative' }}>
                         <Toolbar>
                              <IconButton
                                   edge="start"
                                   color="inherit"
                                   onClick={handleClose}
                                   aria-label="close"
                              >
                                   <Close />
                              </IconButton>
                              <Typography sx={{ ml: 2, flex: 1 }} variant="h6" component="div">
                                   LOGS
                              </Typography>
                         </Toolbar>
                    </AppBar>
                    <DialogTitle id="scroll-dialog-title">{workflowName}</DialogTitle>
                    <DialogContent dividers={scroll === 'paper'}>
                         <DialogContentText
                              id="scroll-dialog-description"
                              ref={descriptionElementRef}
                              tabIndex={-1}
                         >
                              <Typography variant="caption" display="block" gutterBottom style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                                   {contentLog}
                              </Typography>

                         </DialogContentText>
                    </DialogContent>
               </Dialog>

          </React.Fragment >
     );
}

export default NBQueueSideBarComponent;
<CssBaseline />