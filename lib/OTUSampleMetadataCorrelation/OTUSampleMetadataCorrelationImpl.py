# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import time
import shutil
import uuid
import subprocess
import sys

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.DataFileUtilClient import DataFileUtil


from .util.config import Var, reset_Var
from .util.dprint import dprint
from .util.kbase_obj import AmpliconMatrix, AttributeMapping
from .util.params import Params
from .util.error import * # custom exceptions


####################################################################################################
####################################################################################################
def run_check(cmd: str): 
    logging.info('Running cmd `%s`' % cmd)
    t0 = time.time()
    
    # TODO remove shell
    completed_proc = subprocess.run(cmd, shell=True, executable='/bin/bash', stdout=sys.stdout, stderr=sys.stderr)

    t = time.time() - t0
    
    logging.info('Cmd took %.2fmin and returned %d' % ((t/60),completed_proc.returncode))

    if completed_proc.returncode != 0:
        raise NonZeroReturnException(
            "Command `%s` exited with non-zero return code `%d`. "
            "Check logs for more details" %
            (cmd, completed_proc.returncode)
        )

####################################################################################################
####################################################################################################
#END_HEADER


class OTUSampleMetadataCorrelation:
    '''
    Module Name:
    OTUSampleMetadataCorrelation

    Module Description:
    A KBase module: OTUSampleMetadataCorrelation
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/n1mus/OTUSampleMetadataCorrelation"
    GIT_COMMIT_HASH = "133d1e1fff861b49f735d69f23e4dfd8c0c373ea"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_OTUSampleMetadataCorrelation(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_OTUSampleMetadataCorrelation

        #
        ##
        ### params
        ####
        #####

        logging.info(params)

        params = Params(params) # wrap to handle unforeseen ui behavior

        dprint('type(params)', 'type(params["sample_metadata"])', run=locals())


        #
        ##
        ### globals and directories
        ####
        #####

        # TODO
        '''
        tmp/                                        `shared_folder`
        └── run_otu_sample_metadata_<uuid>/           `run_dir`
            ├── return/                             `return_dir`
            |   ├── cmd.txt
            |   ├── workflow.Rmd
            |   ├── otu_table.tsv
            |   ├── sample_metadata.tsv
            |   └── out/                            `out_dir`
            |       ├── workflow.html
            |       └── 

        '''

        ##
        ## set up globals ds `Var` for this API-method run
        ## which involves making this API-method run's directory structure

        reset_Var() # clear all fields but `debug` and config stuff
        Var.update({
            'params': params,
            'run_dir': os.path.join(self.shared_folder, 'run_cor_' + str(uuid.uuid4())),
            'dfu': DataFileUtil(self.callback_url),
            'kbr': KBaseReport(self.callback_url),
            'warnings': [],
        })

        os.mkdir(Var.run_dir)

        Var.update({
            'return_dir': os.path.join(Var.run_dir, 'return'),
        })

        os.mkdir(Var.return_dir)

        Var.update({
            'out_dir': os.path.join(Var.return_dir, 'output')
        })

        os.mkdir(Var.out_dir)


        #
        ##
        ### obj
        ####
        #####
        
        do_tax_table = None not in [params.getd('tax_field'), params.getd('tax_rank')]


        ## objs ##
        amp_mat = AmpliconMatrix(params['amp_mat_upa'])
        col_attrmap = AttributeMapping(amp_mat.obj['col_attributemapping_ref'], amp_mat, 2)
        if do_tax_table: row_attrmap = AttributeMapping(amp_mat.obj['row_attributemapping_ref'], amp_mat, 1)


        dprint('touch #%s' % os.path.join(Var.run_dir, amp_mat.name)) # debugging
        

        #
        ##
        ### check
        ####
        #####

        amp_mat.check_data_valid()
        col_attrmap.check_sample_metadata_valid()
        if do_tax_table: row_attrmap.check_tax_data_valid()


        #
        ##
        ### write files
        ####
        #####
        
        ## define input flpths ##
        otu_table_flpth = os.path.join(Var.return_dir, 'otu_table.tsv')
        sample_metadata_flpth = os.path.join(Var.return_dir, 'sample_metadata.tsv')
        if do_tax_table: tax_table_flpth = os.path.join(Var.return_dir, 'tax_table.tsv')

        ## write input files ##
        amp_mat.to_otu_table(otu_table_flpth)
        col_attrmap.to_metadata_table(sample_metadata_flpth)
        if do_tax_table: row_attrmap.to_tax_table(tax_table_flpth)

        ## Rmd ##
        rmd_flpth = os.path.join(Var.return_dir, os.path.basename(Var.rmd_flpth))
        shutil.copyfile(Var.rmd_flpth, rmd_flpth)
        


        #
        ##
        ### cmd
        ####
        #####

        out_html_flpth = os.path.join(Var.out_dir, 'workflow.html') # generated from Rmd

        pl = params.cmd_params_l()
        pl.extend([
            "otu_table_flpth='%s'" % otu_table_flpth,
            "metadata_flpth='%s'" % sample_metadata_flpth,
            "out_dir='%s'" % Var.out_dir,
            "mcol=%d" % col_attrmap.attribute_index_1based(Var.params['sample_metadata'][0]),
            "scale='%s'" % amp_mat.obj['scale'],
        ])

        if do_tax_table: pl.extend([
            "tax_table_flpth='%s'" % tax_table_flpth
        ])

        cmd = '''\
R -e "rmarkdown::render('%s', output_format='html_document', clean=FALSE, output_file='%s', params=list(amp_mat_name='%s', %s))"''' \
% (rmd_flpth, out_html_flpth, amp_mat.name, ', '.join(pl))




        #
        ##
        ### run
        ####
        #####

        run_check(cmd)






        #
        ## report
        ###
        ####
        #####

        html_links = [{
            'path': Var.out_dir,
            'name': os.path.basename(out_html_flpth),
        }]

        file_links = [{
            'path': Var.return_dir,
            'name': 'results.zip',
            'description': 'Input, output ..'
        }]

        params_report = {
            'warnings': Var.warnings,
            'html_links': html_links,
            'direct_html_link_index': 0,
            'file_links': file_links,
            'workspace_name': params['workspace_name'],
            'html_window_height': 600,
        }

        report = Var.kbr.create_extended_report(params_report)

        output = {
            'report_name': report['name'],
            'report_ref': report['ref'],
        }       


        #END run_OTUSampleMetadataCorrelation

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_OTUSampleMetadataCorrelation return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
