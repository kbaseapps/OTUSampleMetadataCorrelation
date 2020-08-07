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


def run_check(cmd: str): # TODO time it
    logging.info('Running cmd `%s`' % cmd)
    t0 = time.time()
    
    # TODO remove shell
    completed_proc = subprocess.run(cmd, shell=True, executable='/bin/bash', stdout=sys.stdout, stderr=sys.stderr)

    t = time.time() - t0
    
    logging.info('Took %.2fmin' % (t/60))

    if completed_proc.returncode != 0:
        raise NonZeroReturnException(
            "Command `%s` exited with non-zero return code `%d`. "
            "Check logs for more details" %
            (cmd, completed_proc.returncode)
        )

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

        logging.info(params)

        params = Params(params) # wrap to handle unforeseen ui behavior

        dprint('type(params)', 'type(params["sample_metadata"])', run=locals())


        #
        ##
        ### globals and directories
        ####

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
            └── report/                             `report_dir`
                ├── fig
                |   ├── histogram.png
                |   ├── pie.png
                |   └── sunburst.png
                ├── histogram_plotly.html
                ├── pie_plotly.html
                ├── suburst_plotly.html
                └── report.html
        '''

        ##
        ## set up globals ds `Var` for this API-method run
        ## which involves making this API-method run's directory structure

        reset_Var() # clear all fields but `debug` and config stuff
        Var.update({
            'params': params,
            'run_dir': os.path.join(self.shared_folder, 'run_otu_sample_metadata_' + str(uuid.uuid4())),
            'dfu': DataFileUtil(self.callback_url),
            'kbr': KBaseReport(self.callback_url),
            'warnings': [],
        })

        os.mkdir(Var.run_dir)

        Var.update({
            'return_dir': os.path.join(Var.run_dir, 'return'),
            'report_dir': os.path.join(Var.run_dir, 'report'),
        })

        os.mkdir(Var.return_dir)
        os.mkdir(Var.report_dir)

        Var.update({
            'out_dir': os.path.join(Var.return_dir, 'output')
        })

        os.mkdir(Var.out_dir)



        #
        ##
        ### obj
        ####

        #
        amp_mat = AmpliconMatrix(params['amp_mat_upa'])
        col_attrmap = AttributeMapping(params['col_attrmap_upa'])

        # define input flpths
        otu_table_flpth = os.path.join(Var.return_dir, 'otu_table.tsv')
        sample_metadata_flpth = os.path.join(Var.return_dir, 'sample_metadata.tsv')

        # write input files
        amp_mat.to_otu_table(otu_table_flpth)
        col_attrmap.to_metadata_table(sample_metadata_flpth)



        #
        ##
        ### cmd
        ####

        out_html_flpth = os.path.join(Var.out_dir, 'workflow.html') # generated from Rmd

        pl = params.cmd_params_l()
        pl.extend([
            "otu_table_flpth='%s'" % otu_table_flpth,
            "metadata_flpth='%s'" % sample_metadata_flpth,
            "out_dir='%s'" % Var.out_dir,
            "mcol=%d" % col_attrmap.attribute_index_1based(Var.params['sample_metadata'][0]),
        ])

        cmd = '''\
R -e "rmarkdown::render('%s', output_format='html_document', output_file='%s', params=list(%s))"''' \
% (Var.rmd_flpth, out_html_flpth, ', '.join(pl))


        #
        ##
        ### include extra files
        ####

        shutil.copyfile(Var.rmd_flpth, os.path.join(Var.return_dir, os.path.basename(Var.rmd_flpth)))
        
        with open(os.path.join(Var.return_dir, 'cmd.txt'), 'w') as fh:
            fh.write(cmd)



        #
        ##
        ### run
        ####

        run_check(cmd)






        #
        ## report
        ###
        ####

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
